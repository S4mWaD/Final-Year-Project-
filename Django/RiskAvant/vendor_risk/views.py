from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Vendor, RiskAssessment, Certification, SecurityProfile
from .forms import SignUpForm, VendorOnboardingForm

User = get_user_model()

# Home view
@login_required
def home(request):
    user = request.user
    vendor = Vendor.objects.filter(user=user).first()
    onboarding_complete = False
    
    if vendor:
        # Ensure all critical fields are filled
        required_fields = [vendor.name, vendor.contact_email, vendor.contact_phone, vendor.address]
        onboarding_complete = all(required_fields)
    
    return render(request, 'home.html', {
        'user_role': user.role,
        'onboarding_complete': onboarding_complete
    })

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.is_active = True
            user.organization_name = form.cleaned_data.get('organization_name', '')
            user.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('login')

# Vendor Onboarding View
@login_required
def vendor_onboarding(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    vendor, created = Vendor.objects.get_or_create(user=user, defaults={'name': user.username})
    
    if request.method == 'POST':
        form = VendorOnboardingForm(request.POST, instance=vendor)
        if form.is_valid():
            vendor = form.save(commit=False)

            # Check if certifications should be cleared
            if form.cleaned_data["certified"] == "no":
                vendor.certifications.clear()
            else:
                vendor.save()
                form.save_m2m()  # Save many-to-many field data
            
            messages.success(request, 'Vendor onboarded successfully!')
            return redirect('home')  # Redirect to home/dashboard after success
    else:
        form = VendorOnboardingForm(instance=vendor, initial={'certified': vendor.certified})

    return render(
        request,
        'onboarding.html',
        {
            'user_role': request.user.role,
            'form': form,
            'user': user,
        }
    )

# Other Views
@login_required
def profile(request):
    return render(request, 'profile.html', {'user_role': request.user.role})

@login_required
def alerts(request):
    return render(request, 'alerts.html', {'user_role': request.user.role})

@login_required
def settings(request):
    return render(request, 'settings.html', {'user_role': request.user.role})

@login_required
def dashboard(request):
    vendors = Vendor.objects.all()
    risk_assessments = RiskAssessment.objects.all()
    return render(request, 'dashboard.html', {'user_role': request.user.role, 'vendors': vendors, 'risk_assessments': risk_assessments})

@login_required
def risk_list(request):
    return render(request, 'risk_list.html', {'user_role': request.user.role})

@login_required
def checklist_list(request):
    return render(request, 'checklist_list.html', {'user_role': request.user.role})

@login_required
def compliance(request):
    return render(request, 'compliance.html', {'user_role': request.user.role})

@login_required
def audit_log(request):
    return render(request, 'audit_log.html', {'user_role': request.user.role})

@login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'vendor_list.html', {'user_role': request.user.role, 'vendors': vendors})

@login_required
def risk_assessment(request):
    assessments = RiskAssessment.objects.all()
    return render(request, 'risk_assessment.html', {'user_role': request.user.role, 'assessments': assessments})

def terms(request):
    return render(request, 'terms.html')

def generate_questionnaire(request):
    return render(request, 'questionnaire.html')