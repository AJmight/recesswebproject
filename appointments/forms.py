# appointments/forms.py
from django import forms
from .models import Appointment, TherapistAvailability
from django.contrib.auth import get_user_model

User = get_user_model() # Get the User model dynamically

import datetime
from django.utils import timezone

class AppointmentBookingForm(forms.ModelForm):
    therapist = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.THERAPIST, is_approved=True), # Use User.Role enum
        empty_label="Select a Therapist",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    

    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'})
    )

    class Meta:
        model = Appointment
        # Fields now match the updated Appointment model
        fields = ['therapist', 'date', 'start_time', 'notes']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) # Pop 'user' argument if passed
        super().__init__(*args, **kwargs)

        if self.user and self.user.is_authenticated:
            # Ensure therapist queryset is filtered for approved therapists
            self.fields['therapist'].queryset = User.objects.filter(role='THERAPIST', is_approved=True)

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        therapist = cleaned_data.get('therapist')
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')

        if therapist and date and start_time:
            # Ensure end_time is 30 minutes after start_time
            duration = datetime.timedelta(minutes=30)
            # Combine date and time to perform datetime arithmetic
            start_datetime = datetime.datetime.combine(date, start_time)
            end_datetime = start_datetime + duration
            end_time = end_datetime.time() # Get just the time part

            # Add the calculated end_time to cleaned_data for saving to the model
            cleaned_data['end_time'] = end_time

            # Check therapist's fixed availability (from TherapistAvailability model)
            day_of_week = date.weekday()
            # Check if the requested start_time and calculated end_time fall within ANY of the therapist's availability slots for that day
            available_slots = TherapistAvailability.objects.filter(
                therapist=therapist,
                day_of_week=day_of_week,
                start_time__lte=start_time, # Slot starts before or at requested start_time
                end_time__gte=end_time      # Slot ends after or at calculated end_time
            )

            if not available_slots.exists():
                raise forms.ValidationError("The therapist is not available at this exact time slot on this day.")

            # Check for conflicting appointments
            overlapping = Appointment.objects.filter(
                therapist=therapist,
                date=date,
                start_time__lt=end_time, # Existing appointment starts before new one ends
                end_time__gt=start_time, # Existing appointment ends after new one starts
                status__in=['PENDING', 'CONFIRMED']
            )

            if self.instance and self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise forms.ValidationError("This time slot is already booked for the therapist.")

        return cleaned_data

class TherapistAvailabilityForm(forms.ModelForm):
    class Meta:
        model = TherapistAvailability
        fields = ['day_of_week', 'start_time', 'end_time']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned_data