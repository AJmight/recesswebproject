from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_therapist = False  # only users sign up manually
        if commit:
            user.save()
        return user
