from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import AdminProfile
from reports.models import Report
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponseRedirect
from django.urls import reverse


# Public landing page
def landing_page(request):
    return render(request, 'users/landing_page.html')


# ✅ Super Admin Only Views
super_admin_only = user_passes_test(lambda u: u.is_superuser)

@super_admin_only
def register_admin(request):
    return render(request, 'users/admin_registration_form.html')

@super_admin_only
def manage_roles(request):
    return render(request, 'users/admin_role_management.html')

@super_admin_only
def remove_admin(request):
    return render(request, 'users/deactivate_remove_admin.html')

@super_admin_only
def view_admin_list(request):
    return render(request, 'users/view_admins.html')

@super_admin_only
def view_activity_logs(request):
    return render(request, 'users/view_logs_activity.html')

@login_required
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
