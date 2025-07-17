# appointments/admin.py
from django.contrib import admin
from .models import Appointment, TherapistAvailability # Import the models to register them

admin.site.register(Appointment)
admin.site.register(TherapistAvailability)