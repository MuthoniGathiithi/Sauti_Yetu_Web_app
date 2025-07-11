from django.shortcuts import render
from django.http import Http404
from django.template import TemplateDoesNotExist
import logging

logger = logging.getLogger(__name__)

def resources_view(request):
    print("DEBUG: resources_view was called")  # Debug print
    try:
        return render(request, 'resources/resources.html')
    except TemplateDoesNotExist:
        logger.error("Template resources/resources.html not found")
        print("DEBUG: Template resources/resources.html not found")  # Debug print
        raise Http404("Resources page not found")
    except Exception as e:
        logger.error(f"Error in resources_view: {e}")
        print(f"DEBUG: Error in resources_view: {e}")  # Debug print
        raise Http404("Resources page not found")

def help_view(request):
    print("DEBUG: help_view was called")  # Debug print
    try:
        return render(request, 'resources/help.html')
    except TemplateDoesNotExist:
        logger.error("Template resources/help.html not found")
        print("DEBUG: Template resources/help.html not found")  # Debug print
        raise Http404("Help page not found")
    except Exception as e:
        logger.error(f"Error in help_view: {e}")
        print(f"DEBUG: Error in help_view: {e}")  # Debug print
        raise Http404("Help page not found")

def about_view(request):
    print("DEBUG: about_view was called")  # Debug print
    try:
        return render(request, 'resources/about.html')
    except TemplateDoesNotExist:
        logger.error("Template resources/about.html not found")
        print("DEBUG: Template resources/about.html not found")  # Debug print
        raise Http404("About page not found")
    except Exception as e:
        logger.error(f"Error in about_view: {e}")
        print(f"DEBUG: Error in about_view: {e}")  # Debug print
        raise Http404("About page not found")

