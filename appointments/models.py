# appointments/models.py
from django.db import models
from django.conf import settings # To link to the custom User model

class Appointment(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_appointments')
    therapist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='therapist_appointments')
    # CHANGED: Use DateField for date and TimeField for start/end times
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField() # This will be calculated in the form/view

    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('CONFIRMED', 'Confirmed'),
            ('CANCELLED', 'Cancelled'),
            ('COMPLETED', 'Completed'),
        ],
        default='PENDING'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time'] # Order by date then time
        verbose_name_plural = "Appointments"

    def __str__(self):
        return f"Appointment for {self.client.username} with {self.therapist.username} on {self.date.strftime('%Y-%m-%d')} at {self.start_time.strftime('%H:%M')}"

# This model is correct as is, assuming it's for fixed weekly availability
class TherapistAvailability(models.Model):
    therapist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('therapist', 'day_of_week', 'start_time', 'end_time')
        ordering = ['day_of_week', 'start_time']
        verbose_name_plural = "Therapist Availabilities"

    def __str__(self):
        return f"{self.therapist.username}'s availability on {self.get_day_of_week_display()} from {self.start_time} to {self.end_time}"