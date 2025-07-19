# appointments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
import datetime

# Import models and forms from the current app
from .forms import AppointmentBookingForm, TherapistAvailabilityForm
from .models import Appointment, TherapistAvailability

# Import your custom User model
from django.contrib.auth import get_user_model
User = get_user_model()


# Helper functions (assuming they are defined or imported elsewhere, e.g., in users.views)
# For this file, we'll define them locally if not already.
def is_client(user):
    return user.is_authenticated and user.role == User.Role.CLIENT

def is_therapist(user):
    return user.is_authenticated and user.role == User.Role.THERAPIST

def is_admin(user):
    return user.is_authenticated and user.is_admin


# --- Client Views ---

@login_required
@user_passes_test(is_client, login_url='/users/login/') # Ensure client role
def book_appointment(request):
    """
    Handles the booking of new appointments by clients.
    Can pre-select a therapist if 'therapist_username' is passed in GET parameters.
    """
    initial_data = {}
    therapist_username = request.GET.get('therapist_username')
    if therapist_username:
        try:
            # Get the therapist object to set as initial value
            therapist_obj = User.objects.get(username=therapist_username, role=User.Role.THERAPIST, is_approved=True)
            initial_data['therapist'] = therapist_obj.id # Set initial value using the therapist's ID
        except User.DoesNotExist:
            messages.warning(request, f"Therapist '{therapist_username}' not found or not approved.")

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user
            appointment.save()
            messages.success(request, 'Appointment booked successfully! Pending therapist confirmation.')
            return redirect('appointments:client_appointments')
        else:
            messages.error(request, 'Please correct the errors below.')
    else: # GET request
        form = AppointmentBookingForm(user=request.user, initial=initial_data) # Pass initial data here
    
    return render(request, 'appointments/book_appointment.html', {'form': form})

@login_required
@user_passes_test(is_client, login_url='/users/login/')
def client_appointments(request):
    """
    Displays a list of upcoming and past appointments for the logged-in client.
    """
    current_date = timezone.now().date()
    current_time = timezone.now().time()

    upcoming_appointments = Appointment.objects.filter(
        client=request.user,
        date__gte=current_date
    ).order_by('date', 'start_time')

    past_appointments = Appointment.objects.filter(
        client=request.user,
        date__lt=current_date
    ).order_by('-date', '-start_time')

    today_past_appointments = Appointment.objects.filter(
        client=request.user,
        date=current_date,
        end_time__lt=current_time
    ).order_by('-date', '-start_time')

    past_appointments = (past_appointments | today_past_appointments).distinct()

    return render(request, 'appointments/client_appointments.html', {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    })

@login_required
@user_passes_test(is_client, login_url='/users/login/')
def cancel_appointment(request, pk):
    """
    Allows a client to cancel their own appointments.
    """
    appointment = get_object_or_404(Appointment, pk=pk, client=request.user)
    
    if appointment.status == 'PENDING' or appointment.status == 'CONFIRMED':
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.info(request, 'Appointment has been cancelled.')
    else:
        messages.warning(request, 'This appointment cannot be cancelled (e.g., already completed or previously cancelled).')
    return redirect('appointments:client_appointments')

# --- Therapist Views ---

@login_required
@user_passes_test(is_therapist, login_url='/users/login/')
def therapist_appointments(request):
    """
    Displays a list of upcoming and past appointments for the logged-in therapist.
    """
    current_date = timezone.now().date()
    current_time = timezone.now().time()

    upcoming_appointments = Appointment.objects.filter(
        therapist=request.user,
        date__gte=current_date
    ).order_by('date', 'start_time')

    past_appointments = Appointment.objects.filter(
        therapist=request.user,
        date__lt=current_date
    ).order_by('-date', '-start_time')

    today_past_appointments = Appointment.objects.filter(
        therapist=request.user,
        date=current_date,
        end_time__lt=current_time
    ).order_by('-date', '-start_time')

    past_appointments = (past_appointments | today_past_appointments).distinct()

    return render(request, 'appointments/therapist_appointments.html', {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    })

@login_required
@user_passes_test(is_therapist, login_url='/users/login/')
def manage_appointment_status(request, pk):
    """
    Allows a therapist to update the status of their appointments.
    """
    appointment = get_object_or_404(Appointment, pk=pk, therapist=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED']:
            appointment.status = new_status
            appointment.save()
            messages.success(request, f'Appointment status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status provided.')
    return redirect('appointments:therapist_appointments')

@login_required
@user_passes_test(is_therapist, login_url='/users/login/')
def therapist_set_availability(request):
    """
    Allows a therapist to add and view their recurring availability slots.
    """
    if request.method == 'POST':
        form = TherapistAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.therapist = request.user
            
            existing_slot = TherapistAvailability.objects.filter(
                therapist=request.user,
                day_of_week=availability.day_of_week,
                start_time=availability.start_time,
                end_time=availability.end_time
            ).first()

            if existing_slot:
                messages.info(request, "This exact availability slot already exists.")
            else:
                availability.save()
                messages.success(request, 'Availability added successfully!')
            return redirect('appointments:therapist_set_availability')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TherapistAvailabilityForm()
    
    current_availabilities = TherapistAvailability.objects.filter(therapist=request.user).order_by('day_of_week', 'start_time')
    return render(request, 'appointments/therapist_set_availability.html', {
        'form': form,
        'current_availabilities': current_availabilities
    })

@login_required
@user_passes_test(is_therapist, login_url='/users/login/')
def delete_availability(request, pk):
    """
    Allows a therapist to delete one of their availability slots.
    """
    availability = get_object_or_404(TherapistAvailability, pk=pk, therapist=request.user)
    availability.delete()
    messages.info(request, 'Availability slot deleted.')
    return redirect('appointments:therapist_set_availability')
