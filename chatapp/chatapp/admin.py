from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Message

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_therapist', 'is_staff', 'is_superuser')
    list_filter = ('is_therapist', 'is_staff', 'is_superuser')
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('is_therapist',)}),
    )

admin.site.register(User, UserAdmin)
admin.site.register(Message)
