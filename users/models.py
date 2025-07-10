from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        THERAPIST = 'THERAPIST', _('Mental Health Professional')
        CLIENT = 'CLIENT', _('Regular User')
    
    role = models.CharField(
        max_length=20, 
        choices=Role.choices,
        default=Role.CLIENT
    )
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Matches form
    address = models.CharField(max_length=255, blank=True, null=True)  # Added to match form (note capital A)
    email = models.EmailField(blank=True, null=True)  # Make sure this exists
    
    # Therapist-specific fields
    specialization = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    available_days = models.CharField(max_length=100, blank=True, null=True)
    available_hours_start = models.TimeField(blank=True, null=True)
    available_hours_end = models.TimeField(blank=True, null=True)
    is_accepting_clients = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    def is_therapist(self):
        return self.role == self.Role.THERAPIST
    
    def is_client(self):
        return self.role == self.Role.CLIENT