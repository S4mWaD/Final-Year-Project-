from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import password_validators_help_texts
from django.utils.safestring import mark_safe
from .models import CustomUser

password_help_text = mark_safe('<br>'.join(password_validators_help_texts()))

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
    )
    organization_name = forms.CharField(
        max_length=255,
        required=True,
        label="Organization Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your organization name'}),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter a password'}),
        help_text=password_help_text,  # Now formatted properly
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'organization_name']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
        }
        labels = {
            'username': 'Your Username',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }
        error_messages = {
            'username': {
                'required': 'Please enter a username.',
                'unique': 'This username is already taken.',
            },
            'password2': {
                'password_mismatch': 'The two password fields didn’t match.',
            },
        }
        help_texts = {
            'username': None,
            'password2': None,
        }

    def clean(self):
        cleaned_data = super().clean()
        org_name = cleaned_data.get('organization_name')

        if org_name and len(org_name) < 3:
            self.add_error('organization_name', 'Organization name must be at least 3 characters long.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'User'  # Set default role
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.organization_name = self.cleaned_data['organization_name']
        
        if commit:
            user.save()
        
        return user
