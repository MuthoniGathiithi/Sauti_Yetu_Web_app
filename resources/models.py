from django.db import models

class HelpResource(models.Model):
    name = models.CharField(max_length=100)  # Organization or contact name
    help_type = models.CharField(max_length=100)  # e.g. Mental Health, Legal Aid
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)  # e.g. Nairobi, Kirinyaga
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Create your models here.
