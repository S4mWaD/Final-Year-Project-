from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import password_validators_help_texts
from django.utils.safestring import mark_safe
from .models import CustomUser, Vendor

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

# Vendor Onboarding Form
class VendorOnboardingForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'name', 'vendor_type', 'contact_email', 'contact_phone', 'address',
            'website', 'tax_id', 'business_license', 'years_in_operation',
            'num_employees', 'num_clients', 'annual_revenue', 'certifications',
            'certified', 'auditable', 'insurance_coverage'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter company name'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'Enter contact email'}),
            'contact_phone': forms.TextInput(attrs={'placeholder': 'Enter contact phone'}),
            'address': forms.Textarea(attrs={'placeholder': 'Enter company address', 'rows': 3}),
            'website': forms.URLInput(attrs={'placeholder': 'Enter website URL'}),
            'tax_id': forms.TextInput(attrs={'placeholder': 'Enter tax ID'}),
            'business_license': forms.TextInput(attrs={'placeholder': 'Enter business license'}),
            'years_in_operation': forms.NumberInput(attrs={'min': 0, 'placeholder': 'Years in operation'}),
            'num_clients': forms.NumberInput(attrs={'min': 0, 'placeholder': 'Number of clients worked with'}),
            'annual_revenue': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'placeholder': 'Annual revenue in USD'}),
            'certifications': forms.Textarea(attrs={'placeholder': 'Enter certifications (comma-separated)', 'rows': 2}),
            'insurance_coverage': forms.Textarea(attrs={'placeholder': 'Enter insurance coverage details', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        num_clients = cleaned_data.get('num_clients')
        annual_revenue = cleaned_data.get('annual_revenue')
        
        if num_clients is not None and num_clients < 0:
            self.add_error('num_clients', 'Number of clients cannot be negative.')
        
        if annual_revenue is not None and annual_revenue < 0:
            self.add_error('annual_revenue', 'Annual revenue cannot be negative.')
        
        return cleaned_data
