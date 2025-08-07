from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, date
from django.urls import reverse
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

# Utility function
def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Super Admin Only Views
super_admin_only = user_passes_test(lambda u: u.is_superuser)

@super_admin_only
def super_admin_dashboard(request):
    """Super admin dashboard with comprehensive analytics"""
    # Get date range for analytics
    today = date.today()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Basic statistics
    total_reports = Report.objects.count()
    pending_reports = Report.objects.filter(status='pending').count()
    under_review = Report.objects.filter(status='under_review').count()
    resolved_reports = Report.objects.filter(status='resolved').count()
    critical_reports = Report.objects.filter(priority='critical').count()
    
    # Recent activity
    recent_reports = Report.objects.order_by('-date_reported')[:10]
    recent_logs = SystemLog.objects.order_by('-timestamp')[:10]
    
    # Category breakdown
    category_stats = Report.objects.values('category').annotate(
        count=Count('category')
    ).order_by('-count')
    
    # Monthly trends
    monthly_reports = Report.objects.filter(
        date_reported__gte=last_30_days
    ).extra(
        select={'day': 'date(date_reported)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Admin users
    admin_users = User.objects.filter(is_staff=True).count()
    active_resources = SupportResource.objects.filter(is_active=True).count()
    
    context = {
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'under_review': under_review,
        'resolved_reports': resolved_reports,
        'critical_reports': critical_reports,
        'recent_reports': recent_reports,
        'recent_logs': recent_logs,
        'category_stats': category_stats,
        'monthly_reports': monthly_reports,
        'admin_users': admin_users,
        'active_resources': active_resources,
    }
    return render(request, 'users/super_admin_dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Regular admin dashboard"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('landing_page')
    
    # Get reports assigned to this admin
    assigned_reports = Report.objects.filter(assigned_to=request.user)
    pending_assigned = assigned_reports.filter(status='pending').count()
    in_progress_assigned = assigned_reports.filter(status__in=['under_review', 'investigating']).count()
    
    # Recent activity
    recent_assigned = assigned_reports.order_by('-date_reported')[:5]
    recent_updates = ReportUpdate.objects.filter(
        updated_by=request.user
    ).order_by('-timestamp')[:5]
    
    context = {
        'assigned_reports': assigned_reports.count(),
        'pending_assigned': pending_assigned,
        'in_progress_assigned': in_progress_assigned,
        'recent_assigned': recent_assigned,
        'recent_updates': recent_updates,
    }
    return render(request, 'users/admin_dashboard.html', context)


@super_admin_only
def manage_reports(request):
    """Manage all reports with search and filtering"""
    form = ReportSearchForm(request.GET)
    reports = Report.objects.all().order_by('-date_reported')
    
    # Apply filters
    if form.is_valid():
        if form.cleaned_data['search_query']:
            query = form.cleaned_data['search_query']
            reports = reports.filter(
                Q(description__icontains=query) |
                Q(title__icontains=query) |
                Q(location__icontains=query)
            )
        
        if form.cleaned_data['category']:
            reports = reports.filter(category=form.cleaned_data['category'])
        
        if form.cleaned_data['status']:
            reports = reports.filter(status=form.cleaned_data['status'])
        
        if form.cleaned_data['priority']:
            reports = reports.filter(priority=form.cleaned_data['priority'])
        
        if form.cleaned_data['date_from']:
            reports = reports.filter(date_reported__gte=form.cleaned_data['date_from'])
        
        if form.cleaned_data['date_to']:
            reports = reports.filter(date_reported__lte=form.cleaned_data['date_to'])
        
        if form.cleaned_data['county']:
            reports = reports.filter(county__icontains=form.cleaned_data['county'])
    
    # Pagination
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'total_reports': reports.count(),
    }
    return render(request, 'users/manage_reports.html', context)


@login_required
def report_detail(request, report_id):
    """View and update individual report"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('landing_page')
    
    report = get_object_or_404(Report, report_id=report_id)
    updates = report.updates.all().order_by('-timestamp')
    
    if request.method == 'POST':
        form = ReportUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.report = report
            update.updated_by = request.user
            update.previous_status = report.status
            update.save()
            
            # Update report status
            report.status = update.new_status
            if update.new_status == 'resolved':
                report.resolved_date = timezone.now()
            report.save()
            
            # Log the update
            SystemLog.objects.create(
                level='info',
                action_type='report_updated',
                user=request.user,
                ip_address=get_client_ip(request),
                description=f'Report {report.report_id} updated to {update.new_status}',
                related_report=report
            )
            
            messages.success(request, 'Report updated successfully.')
            return redirect('report_detail', report_id=report_id)
    else:
        form = ReportUpdateForm()
    
    context = {
        'report': report,
        'updates': updates,
        'form': form,
    }
    return render(request, 'users/report_detail.html', context)


@super_admin_only
def manage_roles(request):
    """Manage admin roles and permissions"""
    admin_profiles = AdminProfile.objects.select_related('user').all()
    
    context = {
        'admin_profiles': admin_profiles,
    }
    return render(request, 'users/admin_role_management.html', context)


@super_admin_only
def remove_admin(request):
    """Remove admin user"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            if user != request.user:  # Can't remove self
                username = user.username
                user.delete()
                
                # Log the action
                SystemLog.objects.create(
                    level='warning',
                    action_type='admin_action',
                    user=request.user,
                    ip_address=get_client_ip(request),
                    description=f'Admin user removed: {username}'
                )
                
                messages.success(request, f'Admin {username} removed successfully.')
            else:
                messages.error(request, 'Cannot remove yourself.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    
    return redirect('manage_roles')


@super_admin_only
def view_admin_list(request):
    """View all admin users"""
    admins = User.objects.filter(is_staff=True).select_related('adminprofile')
    
    context = {
        'admins': admins,
    }
    return render(request, 'users/view_admins.html', context)


@super_admin_only
def view_activity_logs(request):
    """View system activity logs"""
    logs = SystemLog.objects.all().order_by('-timestamp')
    
    # Filter by level if specified
    level_filter = request.GET.get('level')
    if level_filter:
        logs = logs.filter(level=level_filter)
    
    # Filter by action type if specified
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action_type=action_filter)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'level_filter': level_filter,
        'action_filter': action_filter,
        'log_levels': SystemLog.LOG_LEVELS,
        'action_types': SystemLog.ACTION_TYPES,
    }
    return render(request, 'users/view_logs_activity.html', context)


@super_admin_only
def analytics_dashboard(request):
    """Analytics and reporting dashboard"""
    # Get date range
    today = date.today()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Basic stats
    total_reports = Report.objects.count()
    reports_this_month = Report.objects.filter(date_reported__gte=last_30_days).count()
    reports_this_week = Report.objects.filter(date_reported__gte=last_7_days).count()
    
    # Status breakdown
    status_stats = Report.objects.values('status').annotate(count=Count('status'))
    
    # Category breakdown
    category_stats = Report.objects.values('category').annotate(count=Count('category')).order_by('-count')
    
    # Priority breakdown
    priority_stats = Report.objects.values('priority').annotate(count=Count('priority'))
    
    # Geographic distribution
    county_stats = Report.objects.exclude(county__isnull=True).exclude(county='').values('county').annotate(count=Count('county')).order_by('-count')[:10]
    
    # Gender breakdown
    gender_stats = Report.objects.exclude(reporter_gender__isnull=True).exclude(reporter_gender='').values('reporter_gender').annotate(count=Count('reporter_gender'))
    
    # Age distribution
    age_ranges = [
        ('Under 18', Report.objects.filter(reporter_age__lt=18).count()),
        ('18-25', Report.objects.filter(reporter_age__gte=18, reporter_age__lte=25).count()),
        ('26-35', Report.objects.filter(reporter_age__gte=26, reporter_age__lte=35).count()),
        ('36-45', Report.objects.filter(reporter_age__gte=36, reporter_age__lte=45).count()),
        ('46+', Report.objects.filter(reporter_age__gte=46).count()),
    ]
    
    # Monthly trends (last 12 months)
    monthly_trends = []
    for i in range(12):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        count = Report.objects.filter(date_reported__range=[month_start, month_end]).count()
        monthly_trends.append({
            'month': month_start.strftime('%B %Y'),
            'count': count
        })
    monthly_trends.reverse()
    
    context = {
        'total_reports': total_reports,
        'reports_this_month': reports_this_month,
        'reports_this_week': reports_this_week,
        'status_stats': status_stats,
        'category_stats': category_stats,
        'priority_stats': priority_stats,
        'county_stats': county_stats,
        'gender_stats': gender_stats,
        'age_ranges': age_ranges,
        'monthly_trends': monthly_trends,
    }
    return render(request, 'users/analytics_dashboard.html', context)


@super_admin_only
def manage_resources(request):
    """Manage support resources"""
    resources = SupportResource.objects.all().order_by('-created_date')
    
    if request.method == 'POST':
        form = SupportResourceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource added successfully.')
            return redirect('manage_resources')
    else:
        form = SupportResourceForm()
    
    context = {
        'resources': resources,
        'form': form,
    }
    return render(request, 'users/manage_resources.html', context)


@super_admin_only
def manage_emergency_contacts(request):
    """Manage emergency contacts"""
    contacts = EmergencyContact.objects.all().order_by('sort_order')
    
    if request.method == 'POST':
        form = EmergencyContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Emergency contact added successfully.')
            return redirect('manage_emergency_contacts')
    else:
        form = EmergencyContactForm()
    
    context = {
        'contacts': contacts,
        'form': form,
    }
    return render(request, 'users/manage_emergency_contacts.html', context)
