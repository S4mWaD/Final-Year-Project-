from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import JsonResponse
from .models import Vendor, Questionnaire, VendorResponse, RiskAssessment, OnboardingQuestionnaire
from .utils import calculate_risk_score, classify_risk
from .forms import SignUpForm, VendorOnboardingForm

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
            user.set_password(form.cleaned_data['password1'])
            user.is_active = True
            user.organization_name = form.cleaned_data.get('organization_name', '')
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
        'organization_name': user.organization_name,
        'role': user.role,
    })

# Onboarding view
def onboarding(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if Vendor.objects.filter(user=user).exists():
        messages.error(request, 'Vendor profile already exists for this user.')
        return redirect('home')

    if request.method == 'POST':
        form = VendorOnboardingForm(request.POST)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = user
            vendor.save()
            
            # Fetch applicable questionnaire rules
            applicable_rules = QuestionnaireRule.objects.filter(
                category=vendor.category,
                requires_certification=vendor.certified,
                min_employees__lte=vendor.num_employees,
                max_employees__gte=vendor.num_employees
            )
            
            # Assign relevant questions
            for rule in applicable_rules:
                for question in rule.question_set.all():
                    SecurityChecklist.objects.create(vendor=vendor, question=question, status="Pending")
            
            messages.success(request, 'Onboarding completed successfully!')
            return redirect('home')
    else:
        form = VendorOnboardingForm()
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
    vendors = Vendor.objects.all()
    return render(request, 'dashboard.html', {'vendors': vendors})

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
