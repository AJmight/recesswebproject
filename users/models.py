
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        THERAPIST = 'THERAPIST', _('Mental Health Professional')
        CLIENT = 'CLIENT', _('Client')
    
    role = models.CharField(
        max_length=20, 
        choices=Role.choices,
        default=Role.CLIENT
    )
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True) # Added unique=True for email
    is_approved = models.BooleanField(
        default=False, 
        help_text="Designates whether the therapist account has been approved by an admin."
    )
    
    # Therapist-specific fields (using 'specialization' as per your form)
    specialization = models.CharField(max_length=100, blank=True, null=True) # Renamed from 'specialty' in previous discussions
    location = models.CharField(max_length=100, blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    available_days = models.CharField(max_length=100, blank=True, null=True) # Example: "Mon,Wed,Fri"
    available_hours_start = models.TimeField(blank=True, null=True)
    available_hours_end = models.TimeField(blank=True, null=True)
    is_accepting_clients = models.BooleanField(default=True)

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser or self.is_staff
    
    @property
    def is_therapist(self):
        return self.role == self.Role.THERAPIST and self.is_approved
    
    @property
    def is_client(self):
        return self.role == self.Role.CLIENT