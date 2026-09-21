from django.core.exceptions import ValidationError
from django.forms import (
    CheckboxInput, DateInput, ModelForm, NumberInput, Select, Textarea, TextInput, URLInput,
)
from django.utils import timezone

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

    def clean_year(self):
        year = self.cleaned_data["year"]
        if year > timezone.now().year:
            raise ValidationError("Tahun penghargaan tidak boleh di masa depan.")
        return year
