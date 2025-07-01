from django.db import models
from django.contrib.auth.models import User

class AdminProfile(models.Model):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('counselor', 'Counselor Admin'),
        ('analyst', 'NGO Analyst'),
        ('readonly', 'Read-Only Admin'),
        ('partner', 'Community Access Partner'),
        ('auditor', 'Auditor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


# Create your models here.
