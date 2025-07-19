# core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse_lazy

# Import the Assessment and UserAssessment models
from assessments.models import Assessment, UserAssessment

User = get_user_model()

# Helper functions (ensure these are consistent with users/views.py)
def is_admin(user):
    return user.is_authenticated and user.role == User.Role.ADMIN

def is_client(user):
    return user.is_authenticated and user.role == User.Role.CLIENT

# Example home view (assuming you have one)
def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

def crisis_support(request):
    return render(request, 'core/crisis.html')


@login_required(login_url=reverse_lazy('users:login'))
def dashboard(request):
    user = request.user
    
    # --- SIMPLIFIED LOGIC: Enforce any completed assessment for clients ---
    if user.is_authenticated and user.role == User.Role.CLIENT:
        # Check if the client has completed ANY assessment
        has_completed_any_assessment = UserAssessment.objects.filter(user=user).exists()
        
        if not has_completed_any_assessment:
            messages.warning(request, 'You must complete at least one assessment before accessing the dashboard.')
            return redirect('assessments:assessment_list') # Redirect to the general assessment list
    # --- END SIMPLIFIED LOGIC ---

    context = {
        'user': user,
        'title': 'Dashboard'
    }

    # Admin dashboard counts (remains the same)
    if user.is_authenticated and user.role == User.Role.ADMIN:
        therapists_pending_approval_count = User.objects.filter(
            role=User.Role.THERAPIST, 
            is_approved=False
        ).count()
        total_therapists_count = User.objects.filter(
            role=User.Role.THERAPIST
        ).count()
        total_clients_count = User.objects.filter(
            role=User.Role.CLIENT
        ).count()

        context.update({
            'therapists_pending_approval_count': therapists_pending_approval_count,
            'total_therapists_count': total_therapists_count,
            'total_clients_count': total_clients_count,
            'is_admin_dashboard': True
        })

    return render(request, 'core/dashboard.html', context)
