from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # Public pages
    path('', views.landing_page, name='landing_page'),
    path('report/', views.report_incident, name='report_form'),
    path('report/success/<uuid:report_id>/', views.report_success, name='report_success'),
    path('track/', views.track_report, name='track_report'),
    path('resources/', views.support_resources, name='support_resources'),
    
    # Authentication
    path('admin/login/', views.super_admin_login, name='super_admin_login'),
    path('admin/logout/', views.logout, name='admin_logout'),
    
    # Admin Dashboards
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('super-admin/dashboard/', admin_views.super_admin_dashboard, name='super_admin_dashboard'),
    
    # Report Management
    path('admin/reports/', admin_views.manage_reports, name='manage_reports'),
    path('admin/reports/<uuid:report_id>/', admin_views.report_detail, name='report_detail'),
    
    # Admin Management (Super Admin Only)
    path('super-admin/register/', views.register_admin, name='register_admin'),
    path('super-admin/roles/', admin_views.manage_roles, name='manage_roles'),
    path('super-admin/remove/', admin_views.remove_admin, name='remove_admin'),
    path('super-admin/admins/', admin_views.view_admin_list, name='view_admin_list'),
    
    # System Management
    path('super-admin/logs/', admin_views.view_activity_logs, name='view_activity_logs'),
    path('super-admin/analytics/', admin_views.analytics_dashboard, name='analytics_dashboard'),
    
    # Resource Management
    path('super-admin/resources/', admin_views.manage_resources, name='manage_resources'),
    path('super-admin/emergency-contacts/', admin_views.manage_emergency_contacts, name='manage_emergency_contacts'),
    
    # Settings
    path('admin/settings/', views.admin_settings, name='admin_settings'),
]
