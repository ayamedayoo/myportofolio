import uuid
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.core.validators import MaxValueValidator, MinValueValidator

class StarrableMixin:
    """Perilaku star yang sama untuk model yang punya ``starred_by`` (Project dan Award).

    Mixin biasa (bukan model abstrak), jadi tidak mengubah tabel maupun migrasi.
    """

    def toggle_star(self, user):
        """Beri star kalau belum, batalkan kalau sudah. Mengembalikan status star terbaru."""
        if self.starred_by.filter(pk=user.pk).exists():
            self.starred_by.remove(user)
            return False
        self.starred_by.add(user)
        return True


class AwardQuerySet(models.QuerySet):
    """Filter daftar award, dipakai bersama oleh API DRF dan endpoint JSON lama."""

    def search(self, query):
        """Cari di nama penghargaan atau penyelenggara. Kata kunci kosong tidak menyaring apa pun."""
        query = (query or "").strip()
        if not query:
            return self
        return self.filter(Q(title__icontains=query) | Q(issuer__icontains=query))

    def at_level(self, level):
        """Saring per tingkat. Nilai yang tidak dikenal diabaikan, bukan menghasilkan error."""
        if level in dict(Award.LEVEL_CHOICES):
            return self.filter(level=level)
        return self

    def starred_by_user(self, user):
        """Hanya award yang diberi star oleh ``user``. Pengunjung anonim mendapat daftar kosong."""
        if not user.is_authenticated:
            return self.none()
        return self.filter(starred_by=user)


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Project(StarrableMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    role = models.CharField(max_length=255)
    started_at = models.DateField()
    ended_at = models.DateField(blank=True, null=True)
    # Satu proyek bisa di-star banyak pengguna, dan satu pengguna bisa mem-star banyak proyek
    starred_by = models.ManyToManyField(User, related_name="starred_projects", blank=True)

    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Award(StarrableMixin, models.Model):
    LEVEL_CHOICES = [
        ('internal', 'Internal Kampus'),
        ('regional', 'Regional'),
        ('national', 'Nasional'),
        ('international', 'Internasional'),
    ]
    PLACEMENT_CHOICES = [
        ('first', 'Juara 1'),
        ('second', 'Juara 2'),
        ('third', 'Juara 3'),
        ('finalist', 'Finalis'),
        ('other', 'Penghargaan Lain'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
    )
    placement = models.CharField(max_length=10, choices=PLACEMENT_CHOICES, default='other')
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='national')
    description = models.TextField(blank=True)
    certificate_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    # Pengguna yang memberi star. Satu pengguna maksimal satu star per award.
    starred_by = models.ManyToManyField(User, related_name="starred_awards", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AwardQuerySet.as_manager()

    class Meta:
        ordering = ['-is_featured', '-year', 'title']

    def __str__(self):
        return self.title

class Achievement(models.Model):
    LEVEL_CHOICES = [
        ('campus', 'Campus'),
        ('national', 'National'),
        ('international', 'International'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='campus')
    achieved_at = models.DateField()

    @property
    def is_top_tier(self):
        return self.level in ['national', 'international']

    def __str__(self):
        return self.title

