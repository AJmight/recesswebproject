# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.db.models import Q 

# Import Assessment and UserAssessment models from the assessments app
from assessments.models import Assessment, UserAssessment

User = get_user_model()

from .forms import (
    UserCreateForm, 
    UserLoginForm,  
    UserProfileForm, 
    AdminUserUpdateForm 
)

def is_admin(user):
    return user.is_authenticated and user.role == User.Role.ADMIN

def is_therapist(user):
    return user.is_authenticated and user.role == User.Role.THERAPIST

def is_client(user):
    return user.is_authenticated and user.role == User.Role.CLIENT

# --- Authentication Views ---

def register(request):
    """Handles user registration. Clients are logged in directly, Therapists await admin approval."""
    if request.method == 'POST':
        form = UserCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            if user.role == User.Role.THERAPIST:
                messages.info(request, 'Your mental health professional account has been created and is awaiting admin approval.')
                return redirect('users:login') 
            else: # Client registration
                login(request, user) # Log in the newly registered client
                messages.success(request, 'Account created successfully!')
                
                # --- SIMPLIFIED LOGIC FOR CLIENT REGISTRATION REDIRECT ---
                messages.info(request, 'Welcome! Please take an assessment to get started.')
                return redirect('assessments:assessment_list') # Redirect to the general assessment list
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserCreateForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    """
    Handles user login with explicit superuser handling.
    Uses custom UserLoginForm for therapist approval check.
    """
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            selected_role = form.cleaned_data.get('role') 

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_superuser:
                    user.role = User.Role.ADMIN
                    user.save(update_fields=['role'])
                
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Login failed. Please check your credentials and selected role.')
            print(form.errors) 
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    """Logs out the current user and redirects to the home page."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('core:home')

# --- User Profile Views ---

@login_required(login_url=reverse_lazy('users:login'))
def profile_view(request):
    return render(request, 'users/profile.html')

@login_required(login_url=reverse_lazy('users:login'))
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
        
    context = {
        'form': form,
        'title': 'Edit Your Profile'
    }
    return render(request, 'users/edit_profile.html', context)

# --- Admin Management Views ---

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def admin_manage_therapists(request):
    therapists = User.objects.filter(role=User.Role.THERAPIST).order_by('is_approved', 'username')
    return render(request, 'users/admin_manage_therapists.html', {'therapists': therapists})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def admin_toggle_therapist_approval(request, pk):
    therapist = get_object_or_404(User, pk=pk, role=User.Role.THERAPIST)
    if request.method == 'POST':
        therapist.is_approved = not therapist.is_approved
        therapist.save()
        status = "approved" if therapist.is_approved else "unapproved"
        messages.success(request, f'Mental Health Professional {therapist.username} has been {status}.')
    return redirect('users:admin_manage_therapists')

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def admin_edit_user(request, pk):
    user_to_edit = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, request.FILES, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user_to_edit.username} updated successfully.')
            if user_to_edit.role == User.Role.THERAPIST:
                return redirect('users:admin_manage_therapists')
            return redirect('core:dashboard') 
        else:
            messages.error(request, 'Error updating user profile.')
    else:
        form = AdminUserUpdateForm(instance=user_to_edit)
    return render(request, 'users/admin_edit_user.html', {'form': form, 'user_to_edit': user_to_edit})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def admin_manage_clients(request):
    clients = User.objects.filter(role=User.Role.CLIENT).order_by('username')
    return render(request, 'users/admin_manage_clients.html', {'clients': clients})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def admin_delete_user(request, pk):
    """
    Allows an admin to delete any user (client or therapist).
    Requires confirmation.
    """
    user_to_delete = get_object_or_404(User, pk=pk)
    
    # Prevent deleting superuser or self
    if user_to_delete.is_superuser:
        messages.error(request, "Cannot delete a superuser account.")
        return redirect('users:admin_manage_clients') # Or appropriate admin management page
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('users:admin_manage_clients')

    if request.method == 'POST':
        # Perform the deletion
        user_to_delete.delete()
        messages.success(request, f"User '{user_to_delete.username}' deleted successfully.")
        
        # Redirect based on the role of the deleted user
        if user_to_delete.role == User.Role.CLIENT:
            return redirect('users:admin_manage_clients')
        elif user_to_delete.role == User.Role.THERAPIST:
            return redirect('users:admin_manage_therapists')
        else: # Fallback for other roles or unexpected scenarios
            return redirect('core:dashboard') 
    
    # For GET request, show a confirmation page
    context = {
        'user_to_delete': user_to_delete,
        'title': f'Confirm Delete User: {user_to_delete.username}'
    }
    return render(request, 'users/admin_confirm_delete_user.html', context)


# --- Client-Facing Views ---

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_client, login_url=reverse_lazy('core:dashboard'))
def therapist_directory(request):
    approved_therapists = User.objects.filter(
        role=User.Role.THERAPIST, 
        is_approved=True
    ).order_by('username')
    
    query = request.GET.get('q')
    if query:
        approved_therapists = approved_therapists.filter(
            Q(username__icontains=query) | 
            Q(specialization__icontains=query) |
            Q(bio__icontains=query) |
            Q(location__icontains=query)
        ).distinct()

    context = {
        'therapists': approved_therapists,
        'query': query,
    }
    return render(request, 'users/therapist_directory.html', context)
