from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):  # Changed to inherit from UserCreationForm
    phone_number = forms.CharField(max_length=15, required=True)
    adress = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'phone_number', 'address', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the automatic help text
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'phone_number', 'email']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['phone_number'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True