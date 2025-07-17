# appointments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone # For current date and time operations
import datetime # For timedelta operations in date/time calculations

# Import forms and models from the current app
from .forms import AppointmentBookingForm, TherapistAvailabilityForm
from .models import Appointment, TherapistAvailability

# --- Client Views ---

@login_required
@user_passes_test(lambda u: u.is_client)
def book_appointment(request):
    """
    Handles the booking of new appointments by clients.
    - Requires user to be logged in.
    - Requires user to have the 'CLIENT' role.
    - Uses AppointmentBookingForm for data validation and initial saving.
    """
    if request.method == 'POST':
        # When processing a POST request, populate the form with submitted data.
        # Pass 'user=request.user' to the form's __init__ method.
        # This allows the form to filter the 'therapist' queryset
        # to only show approved therapists, ensuring clients can only book with validated professionals.
        form = AppointmentBookingForm(request.POST, user=request.user)
        if form.is_valid():
            # Save the form data but don't commit to the database yet.
            # The form's clean method has already calculated 'end_time'.
            appointment = form.save(commit=False)
            appointment.client = request.user # Assign the logged-in client to the appointment
            appointment.save() # Now save the appointment to the database
            messages.success(request, 'Appointment booked successfully! Pending therapist confirmation.')
            return redirect('appointments:client_appointments') # Redirect to the client's appointments list
        else:
            # If form is not valid, display error messages to the user.
            messages.error(request, 'Please correct the errors below.')
    else:
        # For a GET request, create an empty form instance.
        # Pass 'user=request.user' for initial queryset filtering.
        form = AppointmentBookingForm(user=request.user)
    return render(request, 'appointments/book_appointment.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_client)
def client_appointments(request):
    """
    Displays a list of upcoming and past appointments for the logged-in client.
    - Requires user to be logged in.
    - Requires user to have the 'CLIENT' role.
    """
    # Get current date and time for comparison
    current_date = timezone.now().date()
    current_time = timezone.now().time()

    # Filter for upcoming appointments:
    # Appointments where the date is in the future, OR
    # appointments where the date is today AND the start_time is in the future.
    upcoming_appointments = Appointment.objects.filter(
        client=request.user,
        date__gte=current_date # Date is today or in the future
    ).order_by('date', 'start_time') # Order by date then by start time

    # Filter for past appointments:
    # Appointments where the date is in the past, OR
    # appointments where the date is today AND the end_time has already passed.
    past_appointments = Appointment.objects.filter(
        client=request.user,
        date__lt=current_date # Date is in the past
    ).order_by('-date', '-start_time') # Order by most recent past first

    # Also include appointments from the current day that have already ended
    today_past_appointments = Appointment.objects.filter(
        client=request.user,
        date=current_date, # Date is today
        end_time__lt=current_time # End time has passed
    ).order_by('-date', '-start_time')

    # Combine the two sets of past appointments and remove duplicates
    # The '|' operator performs a SQL UNION, and .distinct() ensures no duplicates.
    past_appointments = (past_appointments | today_past_appointments).distinct()

    return render(request, 'appointments/client_appointments.html', {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    })

@login_required
@user_passes_test(lambda u: u.is_client)
def cancel_appointment(request, pk):
    """
    Allows a client to cancel their own appointments.
    - Requires user to be logged in.
    - Requires user to have the 'CLIENT' role.
    - Only allows cancellation if status is 'PENDING' or 'CONFIRMED'.
    """
    # Retrieve the appointment, ensuring it belongs to the logged-in client
    appointment = get_object_or_404(Appointment, pk=pk, client=request.user)
    
    # Check if the appointment is in a cancellable state
    if appointment.status == 'PENDING' or appointment.status == 'CONFIRMED':
        appointment.status = 'CANCELLED' # Update status to CANCELLED
        appointment.save()
        messages.info(request, 'Appointment has been cancelled.')
    else:
        messages.warning(request, 'This appointment cannot be cancelled (e.g., already completed or previously cancelled).')
    return redirect('appointments:client_appointments') # Redirect back to client's appointments list

# --- Therapist Views ---

@login_required
@user_passes_test(lambda u: u.is_therapist)
def therapist_appointments(request):
    """
    Displays a list of upcoming and past appointments for the logged-in therapist.
    - Requires user to be logged in.
    - Requires user to have the 'THERAPIST' role AND be approved by an admin.
    """
    # Similar logic to client_appointments for filtering upcoming/past
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
@user_passes_test(lambda u: u.is_therapist)
def manage_appointment_status(request, pk):
    """
    Allows a therapist to update the status of their appointments (e.g., CONFIRMED, CANCELLED, COMPLETED).
    - Requires user to be logged in.
    - Requires user to have the 'THERAPIST' role AND be approved.
    """
    # Retrieve the appointment, ensuring it belongs to the logged-in therapist
    appointment = get_object_or_404(Appointment, pk=pk, therapist=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status') # Get the new status from the POST data
        # Validate the new status against allowed choices
        if new_status in ['PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED']:
            appointment.status = new_status # Update the appointment status
            appointment.save()
            messages.success(request, f'Appointment status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status provided.')
    return redirect('appointments:therapist_appointments') # Redirect back to therapist's appointments list

@login_required
@user_passes_test(lambda u: u.is_therapist)
def therapist_set_availability(request):
    """
    Allows a therapist to add and view their recurring availability slots.
    - Requires user to be logged in.
    - Requires user to have the 'THERAPIST' role AND be approved.
    """
    if request.method == 'POST':
        form = TherapistAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.therapist = request.user # Assign the logged-in therapist
            
            # Check for existing exact slot to prevent duplicates
            existing_slot = TherapistAvailability.objects.filter(
                therapist=request.user,
                day_of_week=availability.day_of_week,
                start_time=availability.start_time,
                end_time=availability.end_time
            ).first() # .first() returns the first object or None if not found

            if existing_slot:
                messages.info(request, "This exact availability slot already exists.")
            else:
                availability.save()
                messages.success(request, 'Availability added successfully!')
            return redirect('appointments:therapist_set_availability') # Redirect to same page to add more
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TherapistAvailabilityForm()
    
    # Retrieve and display current availability slots for the therapist
    current_availabilities = TherapistAvailability.objects.filter(therapist=request.user).order_by('day_of_week', 'start_time')
    return render(request, 'appointments/therapist_set_availability.html', {
        'form': form,
        'current_availabilities': current_availabilities
    })

@login_required
@user_passes_test(lambda u: u.is_therapist)
def delete_availability(request, pk):
    """
    Allows a therapist to delete one of their availability slots.
    - Requires user to be logged in.
    - Requires user to have the 'THERAPIST' role AND be approved.
    """
    # Retrieve the availability slot, ensuring it belongs to the logged-in therapist
    availability = get_object_or_404(TherapistAvailability, pk=pk, therapist=request.user)
    availability.delete() # Delete the object
    messages.info(request, 'Availability slot deleted.')
    return redirect('appointments:therapist_set_availability') # Redirect back to availability management page
