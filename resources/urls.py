from django.urls import path
from .views import resources_view, help_view, about_view

app_name = 'resources'

urlpatterns = [
    path('', resources_view, name='resources'),
    path('help/', help_view, name='help'),
    path('about/', about_view, name='about'),
]
