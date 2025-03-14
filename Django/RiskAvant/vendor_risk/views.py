from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Vendor, RiskAssessment, Certification, SecurityProfile, SecurityChecklist, QuestionnaireRules, OnboardingQuestionnaire, VendorResponse,QuestionBank
from .forms import SignUpForm, VendorOnboardingForm, SecurityChecklistForm

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
            if form.cleaned_data["certified"] == "no":
                vendor.certifications.clear()
            else:
                vendor.save()
                form.save_m2m()
            messages.success(request, 'Vendor onboarded successfully!')
            return redirect('home')
    else:
        form = VendorOnboardingForm(instance=vendor, initial={'certified': vendor.certified})

    return render(request, 'onboarding.html', {'user_role': request.user.role, 'form': form, 'user': user})

# Security Questionnaire Generation
@login_required
def generate_questionnaire(request):
    vendor = Vendor.objects.get(user=request.user)

    # Step 1: Fetch all questions that match the vendor type
    assigned_questions = VendorResponse.objects.filter(vendor=vendor)

    if not assigned_questions.exists():
        relevant_questions = QuestionBank.objects.filter(
            vendor_type=vendor.vendor_type,
            min_employees__lte=vendor.num_clients,
            max_employees__gte=vendor.num_clients
        )

        # Step 2: Filter by certifications (if applicable)
        if vendor.certified == "yes":
            relevant_questions = relevant_questions.filter(
                required_certifications__in=vendor.certifications.all()
            )

        # Step 3: Filter by MFA or other security factors (if applicable)
        if hasattr(vendor, 'security_profile'):
            security_profile = vendor.security_profile
            if security_profile.mfa:
                relevant_questions = relevant_questions.filter(requires_mfa=True)

        # 🚀 Ensure at least some questions are assigned
        if not relevant_questions.exists():
            relevant_questions = QuestionBank.objects.all()[:5]  # Assign any 5 questions as a fallback

        # Step 4: Assign the filtered questions to VendorResponse
        for question in relevant_questions:
            VendorResponse.objects.get_or_create(vendor=vendor, question=question, response='N/A')

    assigned_questions = VendorResponse.objects.filter(vendor=vendor)

    return render(request, 'questionnaire.html', {'form_list': assigned_questions})


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
