from django import forms
from django.core.exceptions import ValidationError
from .models import Report, VoiceReport, ReportUpdate, SupportResource, EmergencyContact
import re

class ReportForm(forms.ModelForm):
    """Comprehensive incident reporting form"""
    
    # Additional fields for better UX
    incident_occurred_recently = forms.BooleanField(
        required=False,
        label="Did this incident occur within the last 24 hours?",
        help_text="This helps us prioritize urgent cases"
    )
    
    emergency_assistance_needed = forms.BooleanField(
        required=False,
        label="Do you need immediate emergency assistance?",
        help_text="Check this if you are in immediate danger"
    )
    
    consent_to_process = forms.BooleanField(
        required=True,
        label="I consent to the processing of this report",
        help_text="Your information will be handled confidentially according to our privacy policy"
    )
    
    class Meta:
        model = Report
        fields = [
            'title', 'description', 'category', 'subcategory',
            'location', 'county', 'constituency',
            'reporter_age', 'reporter_gender', 'reporter_contact',
            'incident_date', 'incident_time',
            'perpetrator_known', 'perpetrator_details',
            'witnesses', 'witness_details',
            'photo_evidence', 'document_evidence', 'additional_evidence'
        ]
        
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Please describe what happened in as much detail as you feel comfortable sharing...',
                'class': 'form-input'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Brief title for this report (optional)',
                'class': 'form-input'
            }),
            'subcategory': forms.TextInput(attrs={
                'placeholder': 'More specific category if applicable',
                'class': 'form-input'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Where did this incident occur?',
                'class': 'form-input'
            }),
            'county': forms.Select(attrs={'class': 'form-input'}),
            'constituency': forms.TextInput(attrs={
                'placeholder': 'Constituency (if known)',
                'class': 'form-input'
            }),
            'reporter_age': forms.NumberInput(attrs={
                'min': 1,
                'max': 120,
                'placeholder': 'Your age (optional)',
                'class': 'form-input'
            }),
            'reporter_gender': forms.Select(attrs={'class': 'form-input'}),
            'reporter_contact': forms.TextInput(attrs={
                'placeholder': 'Phone/Email for follow-up (optional)',
                'class': 'form-input'
            }),
            'incident_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
            'incident_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-input'
            }),
            'perpetrator_details': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Description of the perpetrator(s) if known and safe to share',
                'class': 'form-input'
            }),
            'witness_details': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Information about witnesses if any',
                'class': 'form-input'
            }),
            'additional_evidence': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Any additional evidence or information',
                'class': 'form-input'
            }),
            'photo_evidence': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-input'
            }),
            'document_evidence': forms.FileInput(attrs={
                'accept': '.pdf,.doc,.docx,.txt',
                'class': 'form-input'
            }),
        }
        
        labels = {
            'description': 'What happened?',
            'category': 'Type of incident',
            'subcategory': 'Specific category',
            'location': 'Location of incident',
            'county': 'County',
            'constituency': 'Constituency',
            'reporter_age': 'Your age (optional)',
            'reporter_gender': 'Gender (optional)',
            'reporter_contact': 'Contact for follow-up (optional)',
            'incident_date': 'When did this happen?',
            'incident_time': 'Time of incident',
            'perpetrator_known': 'Do you know the perpetrator?',
            'perpetrator_details': 'Perpetrator details',
            'witnesses': 'Were there witnesses?',
            'witness_details': 'Witness information',
            'photo_evidence': 'Photo evidence (optional)',
            'document_evidence': 'Document evidence (optional)',
            'additional_evidence': 'Additional evidence',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make description required
        self.fields['description'].required = True
        self.fields['category'].required = True
        
        # Add county choices (Kenya counties)
        COUNTY_CHOICES = [
            ('', 'Select County'),
            ('nairobi', 'Nairobi'),
            ('mombasa', 'Mombasa'),
            ('kiambu', 'Kiambu'),
            ('nakuru', 'Nakuru'),
            ('machakos', 'Machakos'),
            ('kajiado', 'Kajiado'),
            ('kisumu', 'Kisumu'),
            ('uasin_gishu', 'Uasin Gishu'),
            ('meru', 'Meru'),
            ('kilifi', 'Kilifi'),
            ('kakamega', 'Kakamega'),
            ('murang\'a', 'Murang\'a'),
            ('nyeri', 'Nyeri'),
            ('kirinyaga', 'Kirinyaga'),
            ('nyandarua', 'Nyandarua'),
            ('laikipia', 'Laikipia'),
            ('other', 'Other'),
        ]
        self.fields['county'].widget = forms.Select(choices=COUNTY_CHOICES, attrs={'class': 'form-input'})
        
        # Add help text
        self.fields['reporter_contact'].help_text = "Optional. Only provide if you want us to follow up with you."
        self.fields['photo_evidence'].help_text = "Upload photos if you have evidence (max 10MB)"
        self.fields['document_evidence'].help_text = "Upload documents like medical reports, police reports, etc."
    
    def clean_reporter_contact(self):
        contact = self.cleaned_data.get('reporter_contact')
        if contact:
            # Basic validation for phone or email
            if not (re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', contact) or 
                   re.match(r'^[\+]?[0-9\s\-\(\)]{10,15}$', contact)):
                raise ValidationError("Please enter a valid phone number or email address")
        return contact
    
    def clean_photo_evidence(self):
        photo = self.cleaned_data.get('photo_evidence')
        if photo:
            if photo.size > 10 * 1024 * 1024:  # 10MB limit
                raise ValidationError("Photo file too large. Maximum size is 10MB.")
        return photo
    
    def clean_document_evidence(self):
        document = self.cleaned_data.get('document_evidence')
        if document:
            if document.size > 20 * 1024 * 1024:  # 20MB limit
                raise ValidationError("Document file too large. Maximum size is 20MB.")
        return document
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set priority based on form responses
        if self.cleaned_data.get('emergency_assistance_needed'):
            instance.priority = 'critical'
        elif self.cleaned_data.get('incident_occurred_recently'):
            instance.priority = 'high'
        
        # Set anonymous status
        if not self.cleaned_data.get('reporter_contact'):
            instance.is_anonymous = True
        else:
            instance.is_anonymous = False
        
        if commit:
            instance.save()
        return instance


class VoiceReportForm(forms.ModelForm):
    """Form for uploading voice reports"""
    
    class Meta:
        model = VoiceReport
        fields = ['audio_file']
        
        widgets = {
            'audio_file': forms.FileInput(attrs={
                'accept': 'audio/*',
                'class': 'form-input'
            })
        }
        
        labels = {
            'audio_file': 'Upload Audio Recording'
        }
    
    def clean_audio_file(self):
        audio = self.cleaned_data.get('audio_file')
        if audio:
            # Check file size (max 50MB)
            if audio.size > 50 * 1024 * 1024:
                raise ValidationError("Audio file too large. Maximum size is 50MB.")
            
            # Check file type
            allowed_types = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/m4a']
            if hasattr(audio, 'content_type') and audio.content_type not in allowed_types:
                raise ValidationError("Unsupported audio format. Please use MP3, WAV, or M4A.")
        
        return audio


class ReportUpdateForm(forms.ModelForm):
    """Form for admin updates on reports"""
    
    class Meta:
        model = ReportUpdate
        fields = ['new_status', 'notes', 'is_public']
        
        widgets = {
            'new_status': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Update notes...',
                'class': 'form-input'
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-checkbox'})
        }
        
        labels = {
            'new_status': 'Update Status',
            'notes': 'Update Notes',
            'is_public': 'Visible to Reporter'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].required = True


class SupportResourceForm(forms.ModelForm):
    """Form for managing support resources"""
    
    class Meta:
        model = SupportResource
        fields = [
            'name', 'description', 'resource_type',
            'contact_phone', 'contact_email', 'website',
            'address', 'county', 'is_24_7', 'is_free',
            'languages_supported', 'is_active'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-input'}),
            'resource_type': forms.Select(attrs={'class': 'form-input'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-input'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-input'}),
            'website': forms.URLInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'county': forms.TextInput(attrs={'class': 'form-input'}),
            'languages_supported': forms.TextInput(attrs={'class': 'form-input'}),
        }


class EmergencyContactForm(forms.ModelForm):
    """Form for managing emergency contacts"""
    
    class Meta:
        model = EmergencyContact
        fields = [
            'name', 'phone_number', 'description',
            'is_24_7', 'is_toll_free', 'languages',
            'coverage_area', 'is_active', 'sort_order'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'languages': forms.TextInput(attrs={'class': 'form-input'}),
            'coverage_area': forms.TextInput(attrs={'class': 'form-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class ReportSearchForm(forms.Form):
    """Form for searching and filtering reports"""
    
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search reports...',
            'class': 'form-input'
        })
    )
    
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + Report.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Report.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    
    priority = forms.ChoiceField(
        required=False,
        choices=[('', 'All Priorities')] + Report.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input'
        })
    )
    
    county = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'County',
            'class': 'form-input'
        })
    )


class AnonymousReportTrackingForm(forms.Form):
    """Form for anonymous users to track their reports"""
    
    report_id = forms.UUIDField(
        label="Report ID",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your report ID',
            'class': 'form-input'
        }),
        help_text="Enter the unique ID provided when you submitted your report"
    )
