from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponse
from .models import Vendor, Questionnaire
from .utils import calculate_risk_score, classify_risk
from .forms import SignUpForm

User = get_user_model()

# Home view
def home(request):
    return render(request, 'home.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
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
            user.set_password(form.cleaned_data['password1'])  # Ensure password is hashed
            user.is_active = True  # Ensure user is active
            user.organization_name = form.cleaned_data.get('organization_name', '')  # Save organization name
            user.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

# User profile view
def profile(request):
    user = request.user
    return render(request, 'profile.html', {
        'username': user.username,
        'email': user.email,
        'organization_name': user.organization_name,  # Include organization name
        'role': user.role,
    })

# Onboarding view
def onboarding(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = SignUpForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Onboarding completed successfully!')
            return redirect('home')
    else:
        form = SignUpForm(instance=user)
    return render(request, 'onboarding.html', {'form': form, 'user': user})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('login')

# Placeholder views for additional pages
def alerts(request):
    return render(request, 'alerts.html')

def settings(request):
    return render(request, 'settings.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def risk_list(request):
    return render(request, 'risk_list.html')

def checklist_list(request):
    return render(request, 'checklist_list.html')

def compliance(request):
    return render(request, 'compliance.html')

def audit_log(request):
    return render(request, 'audit_log.html')

def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'vendor_list.html', {'vendors': vendors})

def risk_assessment(request):
    return render(request, 'risk_assessment.html')