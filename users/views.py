from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AdminProfile
from reports.models import Report
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

# ✅ Admin login view
def admin_login(request):
    if request.method == 'POST':  # ✅ FIX: should be request.method, not request == 'POST'
        username = request.POST.get('username')  # ✅ FIX: corrected syntax
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                user.adminprofile  # This will raise an error if AdminProfile doesn't exist
                login(request, user)
                return redirect('admin_dashboard')
            except AdminProfile.DoesNotExist:
                messages.error(request, "Access Denied - Not an admin.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'users/admin_login.html')


# ✅ Admin dashboard view
@login_required
def admin_dashboard(request):
    try:
        admin_profile = request.user.adminprofile
    except AdminProfile.DoesNotExist:
        messages.error(request, "Access Denied - Admin profile not found.")
        return redirect('admin_login')

    role = admin_profile.role

    # ✅ Stats
    total_reports = Report.objects.count()
    pending_reports = Report.objects.filter(status='pending').count()
    recent_reports = Report.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    # ✅ Context dictionary for the template
    context = {
        'admin_profile': admin_profile,
        'role': role,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'recent_reports': recent_reports,
    }

    return render(request, 'users/admin_dashboard.html', context)


def landing_page(request):
    return render(request, 'users/landing_page.html')

