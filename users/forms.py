
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class UserCreateForm(UserCreationForm): # Renamed from UserRegistrationForm
    # These fields are explicitly defined for customization/ordering in the form
    # They will map to the User model fields
    phone_number = forms.CharField(max_length=20, required=True)
    address = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True) # Max length from AbstractUser
    last_name = forms.CharField(max_length=150, required=True) # Max length from AbstractUser
    role = forms.ChoiceField(choices=User.Role.choices, required=True) # Use User.Role.choices
    specialization = forms.CharField(max_length=100, required=False) # Matches model field name
    bio = forms.CharField(widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)

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
            'specialization', # Matches model field name
            'bio',
            'profile_picture',
        ] + list(UserCreationForm.Meta.fields) # Include password fields from parent

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].help_text = None # Remove help text for password confirmation
        
        # Make specialization required only for therapists based on initial data or post data
        if 'role' in self.data: # Check if role is in POST data
            if self.data['role'] == User.Role.THERAPIST:
                self.fields['specialization'].required = True
        elif self.initial.get('role') == User.Role.THERAPIST: # Check if role is in initial data (for existing instances, though this is a creation form)
            self.fields['specialization'].required = True

    def clean(self):
        cleaned_data = super().clean()
        # UserCreationForm handles password1/password2 matching by default
        
        # Additional validation for therapists
        if cleaned_data.get('role') == User.Role.THERAPIST and not cleaned_data.get('specialization'):
            self.add_error('specialization', "Specialization is required for mental health professionals.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set is_approved to False for therapists by default
        if user.role == User.Role.THERAPIST:
            user.is_approved = False
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
            # Fields below are therapist-specific and should not be editable by clients
            # They will be conditionally displayed/disabled in the template or via __init__
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
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable fields based on user role for their own profile edit
        if self.instance.is_client:
            # Hide/disable therapist-specific fields for clients
            therapist_fields = [
                'specialization', 'location', 'qualifications', 'experience_years',
                'hourly_rate', 'available_days', 'available_hours_start',
                'available_hours_end', 'is_accepting_clients'
            ]
            for field_name in therapist_fields:
                if field_name in self.fields:
                    del self.fields[field_name] # Remove from form for clients

        elif self.instance.is_therapist:
            # Therapists can edit their specific fields
            pass # No fields are disabled by default for therapists editing their own profile

        # Ensure email is not required if it's already set and not being changed
        # This prevents issues if email is optional in your model but required by default in form
        if self.instance.email:
            self.fields['email'].required = False


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
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Only allow role changes for non-superusers (superusers manage their own superuser status)
        if self.instance and self.instance.is_superuser:
            self.fields['role'].disabled = True
        else:
            self.fields['role'].disabled = False # Ensure it's enabled for non-superusers

        # Add help texts for admin-specific fields
        self.fields['is_approved'].help_text = 'Approve this therapist account'
        self.fields['is_active'].help_text = 'Designates whether this user should be treated as active'
        self.fields['is_staff'].help_text = 'Designates whether the user can log into this admin site'
        self.fields['is_superuser'].help_text = 'Designates that this user has all permissions without explicitly assigning them'

        # Only show approval field for therapists
        if self.instance.role != User.Role.THERAPIST:
            if 'is_approved' in self.fields:
                del self.fields['is_approved']

        # Hide therapist-specific fields if the user is not a therapist
        if self.instance.role != User.Role.THERAPIST:
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
    role = forms.ChoiceField(choices=User.Role.choices, required=True)

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
        if not user.is_superuser and user.role != selected_role:
             raise forms.ValidationError(
                 f'You are registered as a {user.get_role_display()}. Please select your correct role.',
                 code='invalid_role',
             )