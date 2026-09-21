import uuid
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

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

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    role = models.CharField(max_length=255)
    started_at = models.DateField()
    ended_at = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Award(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-year', 'title']

    def __str__(self):
        return self.title
