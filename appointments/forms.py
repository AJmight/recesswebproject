from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import profile 

class userRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    phoneNumber = forms.CharField(max_length=15, required=True)
    Adress = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'phoneNumber','Adress','email', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
class userupdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'phoneNumber', 'email']

    def __init__(self, *args, **kwargs):
        super(userupdateForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['phoneNumber'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True