from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('other', 'Other'),
    ]

    admin = models.ForeignKey(User, on_delete=models.CASCADE)  # The admin who did the action
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_model = models.CharField(max_length=100, blank=True, null=True)  # What they acted on (e.g. "Report")
    target_id = models.PositiveIntegerField(blank=True, null=True)  # ID of the thing they touched
    description = models.TextField(blank=True)  # Optional details about what they did
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username} - {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

# Create your models here.
