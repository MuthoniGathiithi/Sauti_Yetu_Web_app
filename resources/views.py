from django.shortcuts import render
from django.http import Http404
from django.template import TemplateDoesNotExist
import logging

logger = logging.getLogger(__name__)

def resources_view(request):
    print(f"DEBUG: resources_view was called with path: {request.path}")
    try:
        print("DEBUG: Attempting to render resources/resources.html")
        response = render(request, 'resources/resources.html')
        print("DEBUG: Successfully rendered resources/resources.html")
        return response
    except TemplateDoesNotExist as e:
        logger.error(f"Template resources/resources.html not found. Error: {str(e)}")
        print(f"DEBUG: Template resources/resources.html not found. Error: {str(e)}")
        raise Http404("Resources page not found")
    except Exception as e:
        logger.error(f"Error in resources_view: {str(e)}")
        print(f"DEBUG: Error in resources_view: {str(e)}")
        raise Http404("Resources page not found")

def help_view(request):
    print(f"DEBUG: help_view was called with path: {request.path}")
    try:
        print("DEBUG: Attempting to render resources/help.html")
        response = render(request, 'resources/help.html')
        print("DEBUG: Successfully rendered resources/help.html")
        return response
    except TemplateDoesNotExist as e:
        logger.error(f"Template resources/help.html not found. Error: {str(e)}")
        print(f"DEBUG: Template resources/help.html not found. Error: {str(e)}")
        raise Http404("Help page not found")
    except Exception as e:
        logger.error(f"Error in help_view: {str(e)}")
        print(f"DEBUG: Error in help_view: {str(e)}")
        raise Http404("Help page not found")

def about_view(request):
    print(f"DEBUG: about_view was called with path: {request.path}")
    try:
        print("DEBUG: Attempting to render resources/about.html")
        response = render(request, 'resources/about.html')
        print("DEBUG: Successfully rendered resources/about.html")
        return response
    except TemplateDoesNotExist as e:
        logger.error(f"Template resources/about.html not found. Error: {str(e)}")
        print(f"DEBUG: Template resources/about.html not found. Error: {str(e)}")
        raise Http404("About page not found")
    except Exception as e:
        logger.error(f"Error in about_view: {str(e)}")
        print(f"DEBUG: Error in about_view: {str(e)}")
        raise Http404("About page not found")

