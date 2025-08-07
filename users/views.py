from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, date
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import AdminProfile
from reports.models import (
    Report, ReportUpdate, SupportResource, ReportAnalytics, 
    SystemLog, EmergencyContact, VoiceReport
)
from reports.forms import (
    ReportForm, ReportUpdateForm, SupportResourceForm, 
    EmergencyContactForm, ReportSearchForm, AnonymousReportTrackingForm
)


# Public landing page
def landing_page(request):
    """Main landing page with statistics"""
    # Get some basic statistics for the landing page
    total_reports = Report.objects.count()
    resolved_reports = Report.objects.filter(status='resolved').count()
    active_resources = SupportResource.objects.filter(is_active=True).count()
    emergency_contacts = EmergencyContact.objects.filter(is_active=True).count()
    
    context = {
        'total_reports': total_reports,
        'resolved_reports': resolved_reports,
        'active_resources': active_resources,
        'emergency_contacts': emergency_contacts,
    }
    return render(request, 'users/landing_page.html', context)


# Report submission and tracking
def report_incident(request):
    """Submit a new incident report"""
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save()
            
            # Log the report creation
            SystemLog.objects.create(
                level='info',
                action_type='report_created',
                user=request.user if request.user.is_authenticated else None,
                ip_address=get_client_ip(request),
                description=f'New report created: {report.report_id}',
                related_report=report
            )
            
            # Show success message with report ID
            messages.success(
                request, 
                f'Your report has been submitted successfully. Your report ID is: {report.report_id}. '
                'Please save this ID to track your report status.'
            )
            
            return redirect('report_success', report_id=report.report_id)
    else:
        form = ReportForm()
    
    # Get emergency contacts for the form page
    emergency_contacts = EmergencyContact.objects.filter(is_active=True)[:3]
    
    context = {
        'form': form,
        'emergency_contacts': emergency_contacts,
    }
    return render(request, 'reports/report_form.html', context)


def report_success(request, report_id):
    """Success page after report submission"""
    report = get_object_or_404(Report, report_id=report_id)
    support_resources = SupportResource.objects.filter(is_active=True)[:5]
    
    context = {
        'report': report,
        'support_resources': support_resources,
    }
    return render(request, 'reports/report_success.html', context)


def track_report(request):
    """Track report status anonymously"""
    report = None
    if request.method == 'POST':
        form = AnonymousReportTrackingForm(request.POST)
        if form.is_valid():
            report_id = form.cleaned_data['report_id']
            try:
                report = Report.objects.get(report_id=report_id)
                report.view_count += 1
                report.save()
            except Report.DoesNotExist:
                messages.error(request, 'Report not found. Please check your report ID.')
    else:
        form = AnonymousReportTrackingForm()
    
    context = {
        'form': form,
        'report': report,
    }
    return render(request, 'reports/track_report.html', context)


# Support resources
def support_resources(request):
    """List all support resources"""
    resources = SupportResource.objects.filter(is_active=True).order_by('resource_type', 'name')
    emergency_contacts = EmergencyContact.objects.filter(is_active=True)
    
    # Group resources by type
    resources_by_type = {}
    for resource in resources:
        resource_type = resource.get_resource_type_display()
        if resource_type not in resources_by_type:
            resources_by_type[resource_type] = []
        resources_by_type[resource_type].append(resource)
    
    context = {
        'resources_by_type': resources_by_type,
        'emergency_contacts': emergency_contacts,
    }
    return render(request, 'resources/support_resources.html', context)


# Utility function
def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ✅ Super Admin Only Views
super_admin_only = user_passes_test(lambda u: u.is_superuser)


@super_admin_only
def register_admin(request):
    """Register new admin users"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        username = request.POST.get('username')

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Set staff status based on role
            if role in ['admin', 'super_admin']:
                user.is_staff = True
                if role == 'super_admin':
                    user.is_superuser = True
                user.save()
            
            # Create admin profile
            AdminProfile.objects.create(
                user=user,
                role=role
            )
            
            # Log the action
            SystemLog.objects.create(
                level='info',
                action_type='admin_action',
                user=request.user,
                ip_address=get_client_ip(request),
                description=f'New admin registered: {username} ({role})'
            )
            
            messages.success(request, f"Admin {username} registered successfully!")
            return redirect('super_admin_dashboard')
            
        except Exception as e:
            messages.error(request, f"Error creating admin: {str(e)}")

    return render(request, 'users/admin_registration_form.html')


@super_admin_only
def admin_settings(request):
    return render(request, 'users/admin_settings.html')


@super_admin_only
def admin_reports(request):
    return render(request, 'users/admin_reports.html')


# Super Admin Login View
def admin_dashboard(request):
    return render(request, 'users/super_admin_dashboard.html')

# ✅ Super Admin Login View
def super_admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('super_admin_dashboard')  # or wherever you want to redirect super admin
        else:
            messages.error(request, 'Invalid credentials or not a superuser.')

    return render(request, 'users/super_admin_login_form.html')

@super_admin_only
def admin_settings(request):
    return render(request, 'users/admin_settings.html')

@super_admin_only
def admin_reports(request):
    return render(request, 'users/admin_reports.html')
