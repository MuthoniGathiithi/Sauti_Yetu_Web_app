from django.shortcuts import render

def resources_view(request):
    return render(request, 'resources/resources.html')  # folder structure: templates/resources/resources.html

def help_view(request):
    return render(request, 'resources/help.html')

def about_view(request):
    return render(request, 'resources/about.html')

