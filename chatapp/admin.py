# chatapp/admin.py

from django.contrib import admin
from .models import Message


admin.site.register(Message) # Register only the Message model
