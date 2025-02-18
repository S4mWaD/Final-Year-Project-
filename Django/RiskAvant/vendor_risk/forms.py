from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

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

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'organization_name']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Enter a password'}),
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
            'username': None,  #Removing the default texts
            'password1': None,
            'password2': None,
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'User'  # Set default role
        if commit:
            user.save()
        return user
