from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import password_validators_help_texts
from django.utils.safestring import mark_safe
from .models import CustomUser, Vendor, Certification

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
        help_text="",
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
                'required': '',
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
        user.role = 'User'
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.organization_name = self.cleaned_data['organization_name']

        if commit:
            user.save()

        return user

class VendorOnboardingForm(forms.ModelForm):
    certified = forms.ChoiceField(
        choices=[("yes", "Yes"), ("no", "No")],
        widget=forms.RadioSelect(attrs={'id': 'certified-radio'}),
        label="Do you have certifications?"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        print("Certifications in Form:", list(Certification.objects.values_list('name', flat=True)))
        self.fields['certifications'].queryset = Certification.objects.all()

    certifications = forms.ModelMultipleChoiceField(
        queryset=Certification.objects.none(),  # Initialize as empty
        widget=forms.CheckboxSelectMultiple(attrs={'id': 'certifications-container'}),
        required=False,
        )

    class Meta:
        model = Vendor
        fields = [
            'name', 'vendor_type', 'contact_email', 'contact_phone', 'address',
            'website', 'tax_id', 'business_license', 'years_in_operation',
            'num_clients', 'annual_revenue', 'certified', 'certifications', 'auditable', 'insurance_coverage'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter company name', 'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'Enter contact email', 'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'placeholder': 'Enter contact phone', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'placeholder': 'Enter company address', 'rows': 3, 'class': 'form-control'}),
            'website': forms.URLInput(attrs={'placeholder': 'Enter website URL', 'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'placeholder': 'Enter tax ID', 'class': 'form-control'}),
            'business_license': forms.TextInput(attrs={'placeholder': 'Enter business license', 'class': 'form-control'}),
            'years_in_operation': forms.NumberInput(attrs={'min': 0, 'placeholder': 'Years in operation', 'class': 'form-control'}),
            'num_clients': forms.NumberInput(attrs={'min': 0, 'placeholder': 'Number of clients worked with', 'class': 'form-control'}),
            'annual_revenue': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'placeholder': 'Annual revenue in USD', 'class': 'form-control'}),
            'insurance_coverage': forms.Textarea(attrs={'placeholder': 'Enter insurance coverage details', 'rows': 3, 'class': 'form-control'}),
        }