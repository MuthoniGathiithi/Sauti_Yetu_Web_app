from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_form, name='report_form'),
    path('voice/', views.voice_upload, name='voice_upload'),
    path('voice/ajax/', views.voice_upload_ajax, name='voice_upload_ajax'),
    path('success/', views.report_success, name='report_success'),
    path('confirmation/', views.report_confirmation, name='report_confirmation'),
    path('contact/', views.contact_form, name='contact_form'),
]