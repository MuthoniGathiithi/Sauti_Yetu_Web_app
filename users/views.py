from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import AdminProfile
from reports.models import Report
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


# Public landing page
def landing_page(request):
    return render(request, 'users/landing_page.html')


# ✅ Super Admin Only Views
super_admin_only = user_passes_test(lambda u: u.is_superuser)

@super_admin_only
def register_admin(request):
    return render(request, 'users/register_admin.html')

@super_admin_only
def manage_roles(request):
    return render(request, 'users/admin_roles_management.html')

@super_admin_only
def remove_admin(request):
    return render(request, 'users/deactivate_remove_admin.html')

@super_admin_only
def view_admin_list(request):
    return render(request, 'users/admin_list.html')

@super_admin_only
def view_activity_logs(request):
    return render(request, 'users/view_system_activity.html')

