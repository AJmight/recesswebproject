from django.db import models
from django.utils import timezone
from users.models import User

class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        COMPLETED = 'COMPLETED', 'Completed'
    
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='client_appointments',
        limit_choices_to={'role': User.Role.CLIENT}
    )
    therapist = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='therapist_appointments',
        limit_choices_to={'role': User.Role.THERAPIST}
    )
    date_time = models.DateTimeField()
    duration = models.PositiveIntegerField(default=60)  # in minutes
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_time']
        unique_together = ['therapist', 'date_time']
    
    def __str__(self):
        return f"{self.client.username} with {self.therapist.username} - {self.date_time}"
    
    def end_time(self):
        return self.date_time + timezone.timedelta(minutes=self.duration)