from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Vendor, RiskAssessment, Certification, SecurityProfile, SecurityChecklist, QuestionnaireRules, OnboardingQuestionnaire, VendorResponse,QuestionBank
from .forms import SignUpForm, VendorOnboardingForm, SecurityChecklistForm
from itertools import chain

User = get_user_model()

# Home view
@login_required
def home(request):
    user = request.user
    vendor = Vendor.objects.filter(user=user).first()
    onboarding_complete = False
    submitted_questionnaire = False
    
    if vendor:
        # Ensure all critical fields are filled
        required_fields = [vendor.name, vendor.contact_email, vendor.contact_phone, vendor.address]
        onboarding_complete = all(required_fields)
    
        # check if the questionnaire is submitted
        submitted_questionnaire = VendorResponse.objects.filter(vendor=vendor).exists()

    return render(request, 'home.html', {
        'user_role': user.role,
        'vendor': vendor,
        'onboarding_complete': onboarding_complete
        , 'submitted_questionnaire': submitted_questionnaire
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

@login_required
def calculate_risk(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    responses = VendorResponse.objects.filter(vendor=vendor)

    # Define scoring system for responses
    SCORE_MAPPING = {
        "Yes": 0,       # No risk if best practice is followed
        "No": 10,       # High risk if best practice is NOT followed
        "Partial": 5,   # Medium risk if partially implemented
        "N/A": 0        # No impact if not applicable
    }

    # Calculate total risk score by summing assigned values for each response
    total_risk_score = sum([SCORE_MAPPING.get(response.response, 0) for response in responses])

    # Assign risk level based on total score
    if total_risk_score <= 20:
        risk_level = "Low"
    elif 20 < total_risk_score <= 50:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # Update or create a RiskAssessment entry for the vendor
    risk_assessment, created = RiskAssessment.objects.update_or_create(
        vendor=vendor,
        defaults={'total_risk_score': total_risk_score, 'risk_level': risk_level}
    )

    return render(request, "risk_assessment.html", {"vendor": vendor, "risk_assessment": risk_assessment})



# Vendor Risk Assessment View
@login_required
def risk_assessment(request):
    assessments = RiskAssessment.objects.all()
    return render(request, 'risk_assessment.html', {'user_role': request.user.role, 'assessments': assessments})

# Vendor List View
@login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'vendor_list.html', {'user_role': request.user.role, 'vendors': vendors})


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

# Security Questionnaire Generation@login_required
@login_required
def generate_questionnaire(request):
    vendor = get_object_or_404(Vendor, user=request.user)

    # Handle form submission
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("response_"):
                response_id = key.split("_")[1]  # Extract question ID
                vendor_response = get_object_or_404(VendorResponse, id=response_id)
                vendor_response.response = value
                vendor_response.save()
        messages.success(request, "Responses submitted successfully! Please proceed with your risk assessment")
        return redirect("home")

    # Fetch all assigned questions for this vendor
    assigned_questions = VendorResponse.objects.filter(vendor=vendor)

    # Fetch General & Legal questions missing from the vendor
    missing_general_legal_questions = QuestionBank.objects.filter(
        category__in=["General", "Legal"], 
        vendor_type__isnull=True
    ).exclude(id__in=assigned_questions.values_list("question__id", flat=True))

    # Assign missing General & Legal questions
    for question in missing_general_legal_questions:
        VendorResponse.objects.get_or_create(vendor=vendor, question=question, defaults={"response": "N/A"})

    if not assigned_questions.exists():
        # ✅ Fetch vendor-specific questions
        vendor_specific_questions = QuestionBank.objects.filter(
            vendor_type=vendor.vendor_type,
            min_employees__lte=vendor.num_clients,
            max_employees__gte=vendor.num_clients
        ).distinct()

        # ✅ Fetch General & Legal questions (which apply to all vendors)
        general_legal_questions = QuestionBank.objects.filter(
            category__in=["General", "Legal"], 
            vendor_type__isnull=True
        ).distinct()

        # ✅ Merge without using union()
        relevant_questions = list(chain(vendor_specific_questions, general_legal_questions))

        # ✅ Preserve General & Legal questions during filtering
        if vendor.certified == "yes":
            relevant_questions = [q for q in relevant_questions if 
                q.required_certifications.filter(id__in=vendor.certifications.values_list("id", flat=True)).exists()
            ] + list(general_legal_questions)

        if hasattr(vendor, "security_profile") and vendor.security_profile.mfa:
            relevant_questions = [q for q in relevant_questions if q.requires_mfa] + list(general_legal_questions)

        # ✅ Assign all relevant questions in VendorResponse
        for question in set(relevant_questions):  # Ensures uniqueness
            VendorResponse.objects.get_or_create(vendor=vendor, question=question, defaults={"response": "N/A"})

    # Fetch assigned questions again for display
    assigned_questions = VendorResponse.objects.filter(vendor=vendor)

    return render(request, "questionnaire.html", {"form_list": assigned_questions})

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
