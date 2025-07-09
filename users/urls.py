from django.urls import path
from . import views

urlpatterns = [
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('landing/', views.landing_page, name='landing_page'),
    path('super-admin/register/', views.register_admin, name='register_admin'),
    path('super-admin/roles/', views.manage_roles, name='manage_roles'),
    path('super-admin/remove/', views.remove_admin, name='remove_admin'),
    path('super-admin/admins/', views.view_admin_list, name='admin_list'),
    path('super-admin/logs/', views.view_activity_logs, name='view_logs'),
]


