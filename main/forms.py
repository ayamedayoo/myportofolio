from django.core.exceptions import ValidationError
from django.forms import (
    CheckboxInput, DateInput, ModelForm, NumberInput, Select, Textarea, TextInput, URLInput,
)
from django.utils import timezone
from django.utils.html import strip_tags

from main.models import Award, Project

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "role",
            "started_at",
            "ended_at",
        ]
        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "role": "Peran",
            "started_at": "Tanggal Mulai",
            "ended_at": "Tanggal Selesai",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "role": TextInput(
                attrs={
                    "placeholder": "Frontend Developer",
                    "maxlength": 255,
                }
            ),
            "started_at": DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "ended_at": DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    # Lapisan pertahanan kedua terhadap XSS: tag HTML dibuang sejak data masuk.
    # Pertahanan utamanya tetap escaping saat data ditampilkan.
    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def clean_role(self):
        role = strip_tags(self.cleaned_data["role"]).strip()
        if not role:
            raise ValidationError("Peran tidak boleh hanya berisi tag HTML.")
        return role

    def clean_description(self):
        description = strip_tags(self.cleaned_data["description"]).strip()
        if not description:
            raise ValidationError("Deskripsi tidak boleh hanya berisi tag HTML.")
        return description

    def clean(self):
        cleaned_data = super().clean()
        started_at = cleaned_data.get("started_at")
        ended_at = cleaned_data.get("ended_at")
        if started_at and ended_at and ended_at < started_at:
            self.add_error("ended_at", "Tanggal selesai tidak boleh sebelum tanggal mulai.")
        return cleaned_data


class AwardForm(ModelForm):
    """Form untuk membuat dan mengubah Award.

    Semua field yang bisa diisi user dimasukkan; ``id``, ``created_at``, dan
    ``updated_at`` sengaja tidak ada karena diisi otomatis oleh Django.
    """

    class Meta:
        model = Award
        fields = [
            "title",
            "issuer",
            "year",
            "placement",
            "level",
            "description",
            "certificate_url",
            "is_featured",
        ]
        labels = {
            "title": "Nama Penghargaan",
            "issuer": "Penyelenggara",
            "year": "Tahun",
            "placement": "Peringkat",
            "level": "Tingkat",
            "description": "Cerita Singkat",
            "certificate_url": "Tautan Sertifikat",
            "is_featured": "Sematkan di urutan teratas",
        }
        help_texts = {
            "description": "Opsional. Apa yang kamu buat atau pelajari dari lomba ini?",
            "certificate_url": "Opsional. Link Google Drive, Credly, atau halaman pengumuman.",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "1st Place Business Plan Competition"}),
            "issuer": TextInput(attrs={"placeholder": "Universitas Indonesia"}),
            "year": NumberInput(attrs={"placeholder": "2026", "min": 2000}),
            "placement": Select(),
            "level": Select(),
            "description": Textarea(attrs={"rows": 3, "placeholder": "Ceritakan sedikit tentang lomba ini"}),
            "certificate_url": URLInput(attrs={"placeholder": "https://..."}),
            "is_featured": CheckboxInput(),
        }

    # Lapisan pertahanan kedua terhadap XSS: tag HTML dibuang sejak data masuk.
    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama penghargaan tidak boleh hanya berisi tag HTML.")
        return title

    def clean_issuer(self):
        issuer = strip_tags(self.cleaned_data["issuer"]).strip()
        if not issuer:
            raise ValidationError("Penyelenggara tidak boleh hanya berisi tag HTML.")
        return issuer

    def clean_description(self):
        # Deskripsi boleh kosong, jadi tidak ditolak walaupun hasilnya kosong.
        return strip_tags(self.cleaned_data["description"]).strip()

    def clean_year(self):
        year = self.cleaned_data["year"]
        if year > timezone.now().year:
            raise ValidationError("Tahun penghargaan tidak boleh di masa depan.")
        return year
