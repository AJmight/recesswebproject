# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class UserCreateForm(UserCreationForm): # This is your main registration form
    # These fields are explicitly defined for customization/ordering in the form
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(
    choices=User.Role.choices, 
    required=True, 
    widget=forms.Select(attrs={'class': 'form-select'})  # Changed from RadioSelect to Select
    )
    specialization = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CBT, Trauma Therapy'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}), required=False)
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    # Therapist-specific fields that are optional for clients
    location = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Kampala, Uganda'}))
    qualifications = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), required=False)
    experience_years = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    hourly_rate = forms.DecimalField(max_digits=6, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    available_days = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mon, Wed, Fri'}))
    available_hours_start = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    available_hours_end = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    is_accepting_clients = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'address',
            'email',
            'role',
            'specialization',
            'bio',
            'profile_picture',
            'location',
            'qualifications',
            'experience_years',
            'hourly_rate',
            'available_days',
            'available_hours_start',
            'available_hours_end',
            'is_accepting_clients',
        ] + list(UserCreationForm.Meta.fields) # Include password fields from parent

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].help_text = None # Remove help text for password confirmation
        
        # Conditionally make therapist fields required/visible based on role selection
        # This logic applies to initial form rendering and when data is posted
        current_role = self.initial.get('role') or (self.data.get('role') if 'role' in self.data else None)

        therapist_specific_fields = [
            'specialization', 'location', 'qualifications', 'experience_years',
            'hourly_rate', 'available_days', 'available_hours_start',
            'available_hours_end', 'is_accepting_clients'
        ]

        if current_role != User.Role.THERAPIST:
            for field_name in therapist_specific_fields:
                if field_name in self.fields:
                    self.fields[field_name].required = False
                    # Optionally hide them in the template using JS or CSS, or just let them be optional
        else: # If role is THERAPIST
            self.fields['specialization'].required = True # Specialization is mandatory for therapists
            # Other therapist fields can be required as per your business logic
            # For now, leaving others as required=False as per your original snippet,
            # but you can change them to True if needed.


    def clean(self):
        cleaned_data = super().clean()
        
        # Additional validation for therapists
        if cleaned_data.get('role') == User.Role.THERAPIST:
            if not cleaned_data.get('specialization'):
                self.add_error('specialization', "Specialization is required for mental health professionals.")
            # Add more validation for other therapist-specific fields if they are required
            # e.g., if not cleaned_data.get('qualifications'):
            #     self.add_error('qualifications', "Qualifications are required for therapists.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # The User model's save method will handle setting is_approved based on the role.
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm): # This form is for users to edit their OWN profile
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'address',
            'bio',
            'profile_picture',
            'specialization',
            'location',
            'qualifications',
            'experience_years',
            'hourly_rate',
            'available_days',
            'available_hours_start',
            'available_hours_end',
            'is_accepting_clients',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifications': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_days': forms.TextInput(attrs={'class': 'form-control'}),
            'available_hours_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'available_hours_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_accepting_clients': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure email is not required if it's already set and not being changed
        if self.instance and self.instance.email:
            self.fields['email'].required = False

        # Disable/hide therapist-specific fields for clients
        if self.instance.role == User.Role.CLIENT:
            therapist_fields = [
                'specialization', 'location', 'qualifications', 'experience_years',
                'hourly_rate', 'available_days', 'available_hours_start',
                'available_hours_end', 'is_accepting_clients'
            ]
            for field_name in therapist_fields:
                if field_name in self.fields:
                    self.fields[field_name].widget = forms.HiddenInput() # Hide the field
                    self.fields[field_name].required = False # Make it not required if hidden
                    # Or, if you want to disable but show:
                    # self.fields[field_name].widget.attrs['disabled'] = 'disabled'
                    # self.fields[field_name].required = False

class AdminUserUpdateForm(UserChangeForm): # This form is for ADMINS to edit ANY user
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'address',
            'role',
            'specialization',
            'bio',
            'profile_picture',
            'is_approved',
            'is_active',
            'is_staff',
            'is_superuser',
            'location',
            'qualifications',
            'experience_years',
            'hourly_rate',
            'available_days',
            'available_hours_start',
            'available_hours_end',
            'is_accepting_clients',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifications': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_days': forms.TextInput(attrs={'class': 'form-control'}),
            'available_hours_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'available_hours_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_accepting_clients': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Only allow role changes for non-superusers (superusers manage their own superuser status)
        if self.instance and self.instance.is_superuser:
            if 'role' in self.fields:
                self.fields['role'].disabled = True
        else:
            if 'role' in self.fields:
                self.fields['role'].disabled = False

        # Add help texts for admin-specific fields
        if 'is_approved' in self.fields: self.fields['is_approved'].help_text = 'Approve this therapist account'
        if 'is_active' in self.fields: self.fields['is_active'].help_text = 'Designates whether this user should be treated as active'
        if 'is_staff' in self.fields: self.fields['is_staff'].help_text = 'Designates whether the user can log into this admin site'
        if 'is_superuser' in self.fields: self.fields['is_superuser'].help_text = 'Designates that this user has all permissions without explicitly assigning them'

        # Only show approval field for therapists
        if self.instance and self.instance.role != User.Role.THERAPIST:
            if 'is_approved' in self.fields:
                del self.fields['is_approved']

        # Hide therapist-specific fields if the user is not a therapist
        if self.instance and self.instance.role != User.Role.THERAPIST:
            therapist_fields = [
                'specialization', 'location', 'qualifications', 'experience_years',
                'hourly_rate', 'available_days', 'available_hours_start',
                'available_hours_end', 'is_accepting_clients'
            ]
            for field_name in therapist_fields:
                if field_name in self.fields:
                    del self.fields[field_name]


class UserLoginForm(AuthenticationForm):
    # Add the role field to the login form
    role = forms.ChoiceField(choices=User.Role.choices, required=True, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        # If the user is a superuser, they are always allowed to log in as ADMIN
        if user.is_superuser:
            return
        
        # For non-superusers, check therapist approval
        if user.role == User.Role.THERAPIST and not user.is_approved:
            raise forms.ValidationError(
                'Your therapist account is pending admin approval.',
                code='inactive',
            )
        
        selected_role = self.cleaned_data.get('role')
        if user.role != selected_role: # Check if the user's actual role matches the selected role
            raise forms.ValidationError(
                f'You are registered as a {user.get_role_display()}. Please select your correct role.',
                code='invalid_role',
            )
