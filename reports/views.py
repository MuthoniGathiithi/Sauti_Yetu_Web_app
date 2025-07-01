from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import base64
from .models import Report, VoiceReport

def report_form(request):
    """Main report form page"""
    if request.method == 'POST':
        # Get form data - all fields are optional
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', '')
        location = request.POST.get('location', '').strip()
        age = request.POST.get('age', '')
        photo_evidence = request.FILES.get('photo_evidence')
        
        # Convert age to integer if provided
        age_int = None
        if age:
            try:
                age_int = int(age)
            except ValueError:
                age_int = None
        
        # Create the report
        report = Report.objects.create(
            title=title if title else None,
            description=description if description else None,
            category=category if category else None,
            location=location if location else None,
            age=age_int,
            photo_evidence=photo_evidence
        )
        
        # Store report ID in session for success page
        request.session['report_id'] = report.id
        messages.success(request, 'Your report has been submitted successfully.')
        return redirect('reports:report_success')
    
    # Get category choices for the form
    categories = Report.CATEGORY_CHOICES
    return render(request, 'reports/report_form.html', {'categories': categories})

def voice_upload(request):
    """Voice upload page"""
    if request.method == 'POST':
        audio_file = request.FILES.get('audio_file')
        
        if audio_file:
            # Create voice report
            voice_report = VoiceReport.objects.create(
                audio_file=audio_file
            )
            
            # Store voice report ID in session
            request.session['voice_report_id'] = voice_report.id
            messages.success(request, 'Your voice report has been uploaded successfully.')
            return redirect('reports:report_success')
        else:
            messages.error(request, 'Please select an audio file to upload.')
    
    return render(request, 'reports/voice_upload.html')

@csrf_exempt
def voice_upload_ajax(request):
    """Handle AJAX voice upload from web recording"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            audio_data = data.get('audio_data')
            
            if audio_data:
                # Decode base64 audio data
                format, audio_string = audio_data.split(';base64,')
                ext = format.split('/')[-1]
                audio_file = ContentFile(
                    base64.b64decode(audio_string),
                    name=f'voice_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.{ext}'
                )
                
                # Create voice report
                voice_report = VoiceReport.objects.create(
                    audio_file=audio_file
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Voice report uploaded successfully',
                    'report_id': voice_report.id
                })
            
            return JsonResponse({'success': False, 'message': 'No audio data received'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def report_success(request):
    """Report success page"""
    report_id = request.session.get('report_id')
    voice_report_id = request.session.get('voice_report_id')
    
    # Clear session data
    if 'report_id' in request.session:
        del request.session['report_id']
    if 'voice_report_id' in request.session:
        del request.session['voice_report_id']
    
    context = {
        'report_submitted': bool(report_id),
        'voice_report_submitted': bool(voice_report_id),
    }
    
    return render(request, 'reports/report_success.html', context)

def report_confirmation(request):
    """Optional contact information page"""
    if request.method == 'POST':
        wants_contact = request.POST.get('wants_contact')
        
        if wants_contact == 'yes':
            # Redirect to contact form
            return render(request, 'reports/contact_form.html')
        else:
            # User doesn't want contact, redirect to final success
            messages.success(request, 'Thank you. Your report is completely anonymous.')
            return redirect('reports:report_success')
    
    return render(request, 'reports/report_confirmation.html')

def contact_form(request):
    """Handle optional contact information"""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip()
        preferred_contact = request.POST.get('preferred_contact', '')
        
        # Here you would typically save this to a ContactInfo model
        # or update the most recent report with contact info
        # For now, we'll just show a success message
        
        messages.success(request, 'Thank you. Someone will contact you within 24 hours.')
        return redirect('reports:report_success')
    
    return render(request, 'reports/contact_form.html')

# Create your views here.
