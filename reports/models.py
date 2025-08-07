from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

class Report(models.Model):
    CATEGORY_CHOICES = [
        ('physical', 'Physical Abuse'),
        ('emotional', 'Emotional Abuse'),
        ('sexual', 'Sexual Abuse'),
        ('economic', 'Economic Abuse'),
        ('cyber', 'Cyber Violence'),
        ('stalking', 'Stalking'),
        ('harassment', 'Harassment'),
        ('discrimination', 'Discrimination'),
        ('workplace', 'Workplace Violence'),
        ('domestic', 'Domestic Violence'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    GENDER_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
        ('non_binary', 'Non-binary'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    # Unique identifier for anonymous tracking
    report_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Report Details
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    
    # Location Information
    location = models.CharField(max_length=255, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    constituency = models.CharField(max_length=100, blank=True, null=True)
    
    # Reporter Information (Optional/Anonymous)
    reporter_age = models.PositiveIntegerField(blank=True, null=True)
    reporter_gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    reporter_contact = models.CharField(max_length=255, blank=True, null=True, help_text="Optional contact info for follow-up")
    
    # Incident Details
    incident_date = models.DateTimeField(blank=True, null=True)
    incident_time = models.TimeField(blank=True, null=True)
    perpetrator_known = models.BooleanField(default=False)
    perpetrator_details = models.TextField(blank=True, null=True)
    witnesses = models.BooleanField(default=False)
    witness_details = models.TextField(blank=True, null=True)
    
    # Evidence
    photo_evidence = models.ImageField(upload_to='evidence_photos/', blank=True, null=True)
    document_evidence = models.FileField(upload_to='evidence_documents/', blank=True, null=True)
    additional_evidence = models.TextField(blank=True, null=True)
    
    # System Fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_reports')
    
    # Timestamps
    date_reported = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    resolved_date = models.DateTimeField(blank=True, null=True)
    
    # Follow-up
    requires_followup = models.BooleanField(default=True)
    followup_notes = models.TextField(blank=True, null=True)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    is_anonymous = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date_reported']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['category', 'date_reported']),
            models.Index(fields=['county', 'constituency']),
        ]

    def __str__(self):
        return f"Report {self.report_id} - {self.get_category_display()}"
    
    def get_absolute_url(self):
        return f"/reports/{self.report_id}/"
    
    @property
    def days_since_reported(self):
        return (timezone.now() - self.date_reported).days


class VoiceReport(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='voice_reports')
    audio_file = models.FileField(upload_to='voice_reports/')
    transcription = models.TextField(blank=True, null=True)
    transcription_confidence = models.FloatField(blank=True, null=True)
    language_detected = models.CharField(max_length=10, blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(blank=True, null=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Voice Report for {self.report.report_id}"


class ReportUpdate(models.Model):
    """Track updates and progress on reports"""
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    previous_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20)
    notes = models.TextField()
    is_public = models.BooleanField(default=False, help_text="Visible to reporter")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Update for {self.report.report_id} by {self.updated_by.username}"


class SupportResource(models.Model):
    """Support resources and contacts"""
    RESOURCE_TYPES = [
        ('hotline', 'Crisis Hotline'),
        ('counseling', 'Counseling Service'),
        ('legal', 'Legal Aid'),
        ('medical', 'Medical Support'),
        ('shelter', 'Safe House/Shelter'),
        ('financial', 'Financial Support'),
        ('educational', 'Educational Resource'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    is_24_7 = models.BooleanField(default=False)
    is_free = models.BooleanField(default=True)
    languages_supported = models.CharField(max_length=200, default="English, Swahili")
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['resource_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_resource_type_display()})"


class ReportAnalytics(models.Model):
    """Analytics and statistics tracking"""
    date = models.DateField(unique=True)
    total_reports = models.PositiveIntegerField(default=0)
    pending_reports = models.PositiveIntegerField(default=0)
    resolved_reports = models.PositiveIntegerField(default=0)
    critical_reports = models.PositiveIntegerField(default=0)
    
    # Category breakdown
    physical_abuse = models.PositiveIntegerField(default=0)
    emotional_abuse = models.PositiveIntegerField(default=0)
    sexual_abuse = models.PositiveIntegerField(default=0)
    cyber_violence = models.PositiveIntegerField(default=0)
    other_categories = models.PositiveIntegerField(default=0)
    
    # Demographics
    reports_by_female = models.PositiveIntegerField(default=0)
    reports_by_male = models.PositiveIntegerField(default=0)
    reports_by_youth = models.PositiveIntegerField(default=0)  # Under 25
    
    # Geographic
    top_county = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Report Analytics"
    
    def __str__(self):
        return f"Analytics for {self.date}"


class SystemLog(models.Model):
    """System activity logging"""
    LOG_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    ACTION_TYPES = [
        ('report_created', 'Report Created'),
        ('report_updated', 'Report Updated'),
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('admin_action', 'Admin Action'),
        ('system_error', 'System Error'),
        ('data_export', 'Data Export'),
        ('backup_created', 'Backup Created'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    description = models.TextField()
    related_report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'level']),
            models.Index(fields=['action_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.get_action_type_display()}"


class EmergencyContact(models.Model):
    """Emergency contacts and hotlines"""
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    description = models.TextField()
    is_24_7 = models.BooleanField(default=True)
    is_toll_free = models.BooleanField(default=False)
    languages = models.CharField(max_length=200, default="English, Swahili")
    coverage_area = models.CharField(max_length=200, default="National")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.phone_number}"
