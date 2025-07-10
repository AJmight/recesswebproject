from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentForm

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.user, request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user
            appointment.save()
            messages.success(request, "Appointment booked successfully!")
            return redirect('appointments:appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentForm(request.user)
    return render(request, 'appointments/book.html', {'form': form})

@login_required
def appointment_list(request):
    if request.user.is_therapist():
        appointments = Appointment.objects.filter(therapist=request.user)
    else:
        appointments = Appointment.objects.filter(client=request.user)
    return render(request, 'appointments/list.html', {'appointments': appointments})

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    # Ensure user is either client or therapist for this appointment
    if request.user not in [appointment.client, appointment.therapist] and not request.user.is_admin():
        messages.error(request, "You don't have permission to view this appointment.")
        return redirect('appointments:list')
    
    return render(request, 'appointments/detail.html', {'appointment': appointment})

@login_required
def update_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Permission check
    if request.user not in [appointment.client, appointment.therapist] and not request.user.is_admin():
        messages.error(request, "You don't have permission to update this appointment.")
        return redirect('appointments:list')
    
    if request.method == 'POST':
        form = AppointmentForm(request.user, request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully!")
            return redirect('appointments:detail', pk=appointment.pk)
    else:
        form = AppointmentForm(request.user, instance=appointment)
    
    return render(request, 'appointments/update.html', {'form': form, 'appointment': appointment})

@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Permission check
    if request.user not in [appointment.client, appointment.therapist] and not request.user.is_admin():
        messages.error(request, "You don't have permission to cancel this appointment.")
        return redirect('appointments:list')
    
    if request.method == 'POST':
        appointment.status = Appointment.Status.CANCELLED
        appointment.save()
        messages.info(request, "Appointment has been cancelled.")
        return redirect('appointments:list')
    
    return render(request, 'appointments/cancel_confirm.html', {'appointment': appointment})