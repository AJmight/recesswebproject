# core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import User # Import your custom User model

def home_view(request):
    """
    Renders the main landing page or public home page.
    """
    return render(request, 'core/home.html')

def about_view(request):
    return render(request, 'core/about.html')

def contact_view(request):
    return render(request, 'core/contact.html')

def crisis_support_view(request):
    """
    Renders the crisis support page.
    """
    return render(request, 'core/crisis.html')

@login_required(login_url='users:login')
def dashboard_view(request):
    """
    Renders the user-specific dashboard after login, customized based on user roles.
    """
    context = {}
    if request.user.is_authenticated and request.user.is_admin:
        context['therapists_pending_approval'] = User.objects.filter(role=User.Role.THERAPIST, is_approved=False).count()
        context['total_therapists'] = User.objects.filter(role=User.Role.THERAPIST).count()
        context['total_clients'] = User.objects.filter(role=User.Role.CLIENT).count()
    return render(request, 'core/dashboard.html', context)