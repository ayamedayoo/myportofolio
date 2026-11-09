from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Award, Project


class ProjectSerializer(serializers.ModelSerializer):
    """Kontrak data API Project: representasi JSON sekaligus aturan validasi input.

    ``is_ongoing``, ``star_count``, ``is_starred``, dan ``starred_by_names`` dihitung
    server, jadi hanya bisa dibaca. Relasi ``starred_by`` (daftar id User) tidak dikirim.
    """

    is_ongoing = serializers.BooleanField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "role",
            "started_at", "ended_at", "is_ongoing",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    # Sepadan dengan clean_* di ProjectForm: jalur API tidak menjalankan form,
    # jadi aturan yang sama harus ada di sini.
    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Nama proyek tidak boleh kosong atau hanya berisi tag HTML.")
        return value

    def validate_role(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Peran tidak boleh kosong atau hanya berisi tag HTML.")
        return value

    def validate_description(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Deskripsi tidak boleh kosong atau hanya berisi tag HTML.")
        return value

    def validate(self, attrs):
        # Pada PATCH, field yang tidak dikirim diambil dari data lama.
        started_at = attrs.get("started_at", getattr(self.instance, "started_at", None))
        ended_at = attrs.get("ended_at", getattr(self.instance, "ended_at", None))
        if started_at and ended_at and ended_at < started_at:
            raise serializers.ValidationError(
                {"ended_at": "Tanggal selesai tidak boleh sebelum tanggal mulai."}
            )
        return attrs

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class StarInfoMixin(serializers.Serializer):
    """Field star yang dihitung server dan hanya bisa dibaca.

    ``starred_by`` sebaiknya sudah di-prefetch, jadi ketiga method di bawah
    cukup membaca cache tanpa query tambahan per data.
    Yang dikirim hanya username, bukan email, id, atau password hash.
    """

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    def get_star_count(self, obj):
        return len(obj.starred_by.all())

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return any(user.pk == request.user.pk for user in obj.starred_by.all())

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


def _clean_text(value, message, allow_blank=False):
    """Buang tag HTML seperti ``clean_<field>`` di AwardForm (Tugas 5)."""
    value = strip_tags(value).strip()
    if not value and not allow_blank:
        raise serializers.ValidationError(message)
    return value


class AwardSerializer(StarInfoMixin, serializers.ModelSerializer):
    """Kontrak data API Award: bentuk JSON sekaligus aturan validasi input.

    Field ``*_display`` dan field star dihitung server, jadi hanya bisa dibaca.
    Aturan validasinya sama dengan AwardForm, karena jalur API tidak melewati form.
    """

    placement_display = serializers.CharField(source="get_placement_display", read_only=True)
    level_display = serializers.CharField(source="get_level_display", read_only=True)

    class Meta:
        model = Award
        fields = [
            "id", "title", "issuer", "year",
            "placement", "placement_display", "level", "level_display",
            "description", "certificate_url", "is_featured",
            "star_count", "is_starred", "starred_by_names",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_title(self, value):
        return _clean_text(value, "Nama penghargaan tidak boleh kosong atau hanya berisi tag HTML.")

    def validate_issuer(self, value):
        return _clean_text(value, "Penyelenggara tidak boleh kosong atau hanya berisi tag HTML.")

    def validate_description(self, value):
        # Deskripsi memang opsional, jadi hasil kosong tetap diterima.
        return _clean_text(value, "", allow_blank=True)

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError("Tahun penghargaan tidak boleh di masa depan.")
        return value
