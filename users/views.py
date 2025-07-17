from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

User = get_user_model()

from .forms import (
    UserCreateForm,
    UserLoginForm,
    UserProfileForm,
    AdminUserUpdateForm
)

def is_admin(user):
    """Checks if the user is authenticated and has admin role or is staff/superuser."""
    return user.is_authenticated and user.is_admin

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
            else:
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('core:dashboard')
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
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Explicit superuser handling - treat them as ADMIN regardless of selected role
                if user.is_superuser:
                    user.role = User.Role.ADMIN
                    user.save(update_fields=['role'])
                
                # The UserLoginForm's confirm_login_allowed already handles therapist approval check
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
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
    """Displays the current authenticated user's profile."""
    return render(request, 'users/profile.html')

@login_required(login_url=reverse_lazy('users:login'))
def edit_profile_view(request):
    """Allows the authenticated user to edit their own profile."""
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
    """Allows admins to view and manage therapist accounts (e.g., approve/disapprove)."""
    therapists = User.objects.filter(role=User.Role.THERAPIST).order_by('is_approved', 'username')
    return render(request, 'users/admin_manage_therapists.html', {'therapists': therapists})

@login_required(login_url=reverse_lazy('users:login'))
@user_passes_test(is_admin, login_url=reverse_lazy('core:dashboard'))
def admin_toggle_therapist_approval(request, pk):
    """Toggles the approval status of a therapist."""
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
    """Allows admins to edit any user's profile."""
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
    """
    Allows admins to view and manage client accounts.
    """
    clients = User.objects.filter(role=User.Role.CLIENT).order_by('username')
    return render(request, 'users/admin_manage_clients.html', {'clients': clients})
