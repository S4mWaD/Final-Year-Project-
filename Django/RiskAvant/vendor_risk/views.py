from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Vendor, RiskAssessment, Certification, SecurityProfile, SecurityChecklist, QuestionnaireRules, OnboardingQuestionnaire, VendorResponse,QuestionBank
from .forms import SignUpForm, VendorOnboardingForm, SecurityChecklistForm
from itertools import chain
import json, weasyprint, matplotlib.pyplot as plt, base64, matplotlib
matplotlib.use('Agg')
from io import BytesIO
from django.template.loader import render_to_string
from datetime import datetime

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


# A landing page view to redirect to landing page
def landing_page(request):
    return render(request, 'landing.html')

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

    # Define category weights (in percentages summing up to 100)
    CATEGORY_WEIGHTS = {
        "Technical": 40,
        "Compliance": 20,
        "Legal": 15,
        "General": 15,
        "Operational": 10,
    }

    # Calculate scores for each category
    category_scores = {category: 0 for category in CATEGORY_WEIGHTS}
    category_totals = {category: 0 for category in CATEGORY_WEIGHTS}

    for response in responses:
        category = response.question.category
        score = SCORE_MAPPING.get(response.response, 0)
        category_scores[category] += score
        category_totals[category] += 10  # Maximum possible score per response

    # Calculate weighted scores for each category
    weighted_scores = {}
    for category, total_score in category_scores.items():
        max_possible_score = category_totals[category] or 1  # Prevent division by zero
        weighted_scores[category] = (total_score / max_possible_score) * CATEGORY_WEIGHTS[category]

    # Calculate overall weighted risk score (sum of weighted category scores)
    weighted_risk_score = sum(weighted_scores.values())

    # Assign risk level based on overall weighted risk score
    if weighted_risk_score <= 20:
        risk_level = "Low"
    elif 20 < weighted_risk_score <= 50:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # Update or create a RiskAssessment entry for the vendor
    risk_assessment, created = RiskAssessment.objects.update_or_create(
        vendor=vendor,
        defaults={'total_risk_score': int(weighted_risk_score), 'risk_level': risk_level}
    )

    # Prepare chart data for frontend
    chart_data = {
        "labels": list(weighted_scores.keys()),
        "datasets": [{
            "label": f"Risk Assessment for {vendor.name}",
            "data": list(weighted_scores.values()),
            "backgroundColor": [
                "#4e73df", "#1cc88a", "#36b9cc", "#f6c23e", "#e74a3b"
            ],
            "borderColor": [
                "#2e59d9", "#17a673", "#2c9faf", "#dda20a", "#be2617"
            ],
            "borderWidth": 1,
        }]
    }

    # Convert to JSON format
    chart_data_json = json.dumps(chart_data)

    return render(request, "risk_assessment.html", {
        "vendor": vendor,
        "risk_assessment": risk_assessment,
        "weighted_risk_score": weighted_risk_score,
        "risk_level": risk_level,
        "chart_data": chart_data_json,
    })
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')

    # Gather statistics
    total_vendors = Vendor.objects.count()
    total_responses = VendorResponse.objects.count()
    total_questions = QuestionBank.objects.count()
    total_risk_assessments = RiskAssessment.objects.count()
    total_users = CustomUser.objects.count()

    # Risk Assessment Levels
    low_risk_count = RiskAssessment.objects.filter(risk_level="Low").count()
    medium_risk_count = RiskAssessment.objects.filter(risk_level="Medium").count()
    high_risk_count = RiskAssessment.objects.filter(risk_level="High").count()

    # Print statements for debugging
    print("Low Risk Count:", low_risk_count)
    print("Medium Risk Count:", medium_risk_count)
    print("High Risk Count:", high_risk_count)

    # Chart Data
    chart_data = {
        "labels": ["Low Risk", "Medium Risk", "High Risk"],
        "datasets": [{
            "label": "Risk Assessment Levels",
            "data": [low_risk_count, medium_risk_count, high_risk_count],
            "backgroundColor": ["#28a745", "#ffc107", "#dc3545"]
        }]
    }

    # Convert to JSON format
    chart_data_json = json.dumps(chart_data)
    print("Final Chart Data JSON:", chart_data_json)  # Print the final JSON to verify

    return render(request, 'dashboard.html', {
        'total_vendors': total_vendors,
        'total_responses': total_responses,
        'total_questions': total_questions,
        'total_risk_assessments': total_risk_assessments,
        'total_users': total_users,
        'chart_data': chart_data_json,
    })

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


import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
from .models import Vendor, RiskAssessment, VendorResponse
from django.contrib.auth.decorators import login_required


@login_required
def generate_pdf(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    risk_assessment = RiskAssessment.objects.filter(vendor=vendor).first()

    # Define scoring system for responses
    responses = VendorResponse.objects.filter(vendor=vendor)
    SCORE_MAPPING = {
        "Yes": 0,
        "No": 10,
        "Partial": 5,
        "N/A": 0
    }

    # Category weights
    CATEGORY_WEIGHTS = {
        "Technical": 40,
        "Compliance": 20,
        "Legal": 15,
        "General": 15,
        "Operational": 10,
    }

    # Calculate scores for each category
    category_scores = {category: 0 for category in CATEGORY_WEIGHTS}
    category_totals = {category: 0 for category in CATEGORY_WEIGHTS}

    for response in responses:
        category = response.question.category
        score = SCORE_MAPPING.get(response.response, 0)
        category_scores[category] += score
        category_totals[category] += 10

    # Weighted scores calculation
    weighted_scores = {}
    for category, total_score in category_scores.items():
        max_possible_score = category_totals[category] or 1
        weighted_scores[category] = (total_score / max_possible_score) * CATEGORY_WEIGHTS[category]

    # Overall weighted risk score
    weighted_risk_score = sum(weighted_scores.values())

    # Risk level determination
    if weighted_risk_score <= 20:
        risk_level = "Low"
    elif 20 < weighted_risk_score <= 50:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # 🎨 Generate Pie Chart as a base64 image
    plt.figure(figsize=(6, 6))
    labels = list(weighted_scores.keys())
    sizes = list(weighted_scores.values())
    colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854']

    wedges, texts, autotexts = plt.pie(sizes, colors=colors, autopct='%1.1f%%', startangle=90, textprops=dict(color="white"))
    plt.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.title('Category-wise Risk Scores', pad=20)
    plt.gca().set_aspect('equal', adjustable='box')

    # Save chart to a bytes buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Render HTML template for PDF
    html = render_to_string('risk_assessment_pdf.html', {
        "vendor": vendor,
        "weighted_risk_score": weighted_risk_score,
        "risk_level": risk_level,
        "weighted_scores": weighted_scores,
        "category_weights": CATEGORY_WEIGHTS,
        "responses": responses,
        "chart_image": image_base64,
        "current_date": datetime.now().strftime('%Y-%m-%d'),
        "current_year": datetime.now().year,
    })

    # Generate PDF from HTML
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename={vendor.name}_risk_report.pdf'
    pdf = weasyprint.HTML(string=html).write_pdf()
    response.write(pdf)
    return response