from django.db import models
from django.utils import timezone

class Report(models.Model):
    CATEGORY_CHOICES = [
        ('physical', 'Physical Abuse'),
        ('emotional', 'Emotional Abuse'),
        ('sexual', 'Sexual Abuse'),
        ('economic', 'Economic Abuse'),
        ('cyber', 'Cyber Violence'),
        ('stalking', 'Stalking'),
        ('harassment', 'Harassment'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    photo_evidence = models.ImageField(upload_to='evidence_photos/', blank=True, null=True)
    date_reported = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title or "Anonymous Report"


class VoiceReport(models.Model):
    audio_file = models.FileField(upload_to='voice_reports/')
    transcription = models.TextField(blank=True, null=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Voice Report {self.id}"


# Create your models here.
