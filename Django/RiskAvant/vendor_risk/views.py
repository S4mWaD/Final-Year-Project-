from django.conf import settings
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Vendor, RiskAssessment, Certification, SecurityProfile, SecurityChecklist, QuestionnaireRules, OnboardingQuestionnaire, VendorResponse,QuestionBank, SecurityChecklistTemplate
from .forms import SignUpForm, VendorOnboardingForm, SecurityChecklistForm
from itertools import chain
import json, weasyprint, matplotlib.pyplot as plt, base64, matplotlib
matplotlib.use('Agg')
from io import BytesIO
from django.template.loader import render_to_string
from django.db.models import Q 
from datetime import datetime
from django.templatetags.static import static
from django.utils.timezone import now
import logging 
import re

logger = logging.getLogger(__name__)
User = get_user_model()

# Home view
@login_required
def home(request):
    user = request.user
    vendor = Vendor.objects.filter(user=user).first()
    onboarding_complete = False
    submitted_questionnaire = False
    latest_assessment = None

    if vendor:
        required_fields = [vendor.name, vendor.contact_email, vendor.contact_phone, vendor.address]
        onboarding_complete = all(required_fields)
        submitted_questionnaire = SecurityChecklist.objects.filter(vendor=vendor, response__isnull=False).exists()
        latest_assessment = RiskAssessment.objects.filter(vendor=vendor).order_by('-created_at').first()
        

    if user.is_superuser or user.is_staff:
        # Admin-side stats
        total_vendors = Vendor.objects.count()
        total_responses = SecurityChecklist.objects.count()
        total_questions = SecurityChecklistTemplate.objects.count()
        total_risk_assessments = RiskAssessment.objects.count()
        total_users = CustomUser.objects.count()

        # Risk assessment distribution
        low_risk_count = RiskAssessment.objects.filter(risk_level="Low").count()
        medium_risk_count = RiskAssessment.objects.filter(risk_level="Medium").count()
        high_risk_count = RiskAssessment.objects.filter(risk_level="High").count()

        # Chart data for dashboard
        chart_data = {
            "labels": ["Low Risk", "Medium Risk", "High Risk"],
            "datasets": [{
                "label": "Risk Assessment Levels",
                "data": [low_risk_count, medium_risk_count, high_risk_count],
                "backgroundColor": ["#28a745", "#ffc107", "#dc3545"]
            }]
        }
        chart_data_json = json.dumps(chart_data)

        # ✅ Include 5 most recent risk assessments
        recent_assessments = RiskAssessment.objects.select_related('vendor').order_by('-created_at')[:5]
        vendors = Vendor.objects.select_related("user").prefetch_related(
    "certifications", "risk_assessments", "security_checklists", "responses"
)

        return render(request, 'home_admin.html', {
            'total_vendors': total_vendors,
            'total_responses': total_responses,
            'total_questions': total_questions,
            'total_risk_assessments': total_risk_assessments,
            'total_users': total_users,
            'chart_data': chart_data_json,
            'recent_assessments': recent_assessments,  # ✅ Injected for dashboard table
            'vendors' : vendors, 
        })

    else:
        # Regular user view
        recent_assessments = []
        if vendor:
            recent_assessments = RiskAssessment.objects.filter(vendor=vendor).order_by('-created_at')[:5]

        return render(request, 'home_user.html', {
            'user_role': user.role,
            'vendor': vendor,
            'onboarding_complete': onboarding_complete,
            'submitted_questionnaire': submitted_questionnaire,
            'recent_assessments': recent_assessments,
            'latest_assessment': latest_assessment 
        })

def compute_risk_score(vendor):
    responses = SecurityChecklist.objects.filter(vendor=vendor, response__isnull=False)

    SCORE_MAPPING = {"Yes": 0, "No": 10, "Partial": 5, "N/A": 0}
    CATEGORY_WEIGHTS = {
        "Technical": 40, "Compliance": 20, "Legal": 15,
        "General": 15, "Operational": 10,
    }

    category_scores = {cat: 0 for cat in CATEGORY_WEIGHTS}
    category_totals = {cat: 0 for cat in CATEGORY_WEIGHTS}

    for item in responses:
        # Normalize category to handle spaces and case mismatches
        category = (item.category or "").strip().title()

        # Log to verify if 'Compliance' category is being processed
        if category == "Compliance":
            print(f"[DEBUG] Processing Compliance Question: {item.question}")

        # Fix missing category if not set
        if not item.category:
            template = SecurityChecklistTemplate.objects.filter(question=item.question).first()
            if template:
                item.category = template.category
                item.save(update_fields=["category"])

        if category not in CATEGORY_WEIGHTS:
            continue

        score = SCORE_MAPPING.get(item.response, 0)
        template = SecurityChecklistTemplate.objects.filter(question=item.question).first()
        if template and template.is_critical:
            score *= 1.5

        category_scores[category] += score
        category_totals[category] += 10

    weighted_scores = {
        category: (category_scores[category] / (category_totals[category] or 1)) * CATEGORY_WEIGHTS[category]
        for category in CATEGORY_WEIGHTS
    }

    overall_score = sum(weighted_scores.values())

    if overall_score <= 20:
        risk_level = "Low"
    elif 20 < overall_score <= 50:
        risk_level = "Medium"
    else:
        risk_level = "High"

    RiskAssessment.objects.update_or_create(
        vendor=vendor,
        defaults={
            'total_risk_score': int(overall_score),
            'risk_level': risk_level,
            'created_at': now()
        }
    )




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
    responses = SecurityChecklist.objects.filter(vendor=vendor, response__isnull=False)

    SCORE_MAPPING = {"Yes": 0, "No": 10, "Partial": 5, "N/A": 0}
    CATEGORY_WEIGHTS = {
        "Technical": 40, "Compliance": 20, "Legal": 15,
        "General": 15, "Operational": 10,
    }

    category_scores = {cat: 0 for cat in CATEGORY_WEIGHTS}
    category_totals = {cat: 0 for cat in CATEGORY_WEIGHTS}

    for item in responses:
        # Normalize category to handle spaces and case mismatches
        category = (item.category or "").strip().title()

        if not item.category:
            template = SecurityChecklistTemplate.objects.filter(question=item.question).first()
            if template:
                item.category = template.category
                item.save(update_fields=["category"])

        if category not in CATEGORY_WEIGHTS:
            continue

        score = SCORE_MAPPING.get(item.response, 0)
        template = SecurityChecklistTemplate.objects.filter(question=item.question).first()
        if template and template.is_critical:
            score *= 1.5

        category_scores[category] += score
        category_totals[category] += 10

    weighted_scores = {
        category: (category_scores[category] / (category_totals[category] or 1)) * CATEGORY_WEIGHTS[category]
        for category in CATEGORY_WEIGHTS
    }

    overall_score = sum(weighted_scores.values())

    if overall_score <= 20:
        risk_level = "Low"
    elif 20 < overall_score <= 50:
        risk_level = "Medium"
    else:
        risk_level = "High"

    risk_assessment, created = RiskAssessment.objects.update_or_create(
        vendor=vendor,
        defaults={
            'total_risk_score': int(overall_score),
            'risk_level': risk_level,
            'created_at': now()
        }
    )

    chart_data = {
        "labels": list(weighted_scores.keys()),
        "datasets": [{
            "label": f"Risk Assessment for {vendor.name}",
            "data": list(weighted_scores.values()),
            "backgroundColor": ["#4e73df", "#1cc88a", "#36b9cc", "#f6c23e", "#e74a3b"],
            "borderColor": ["#2e59d9", "#17a673", "#2c9faf", "#dda20a", "#be2617"],
            "borderWidth": 1,
        }]
    }

    return render(request, "risk_assessment.html", {
        "vendor": vendor,
        "risk_assessment": risk_assessment,
        "weighted_risk_score": overall_score,
        "risk_level": risk_level,
        "chart_data": json.dumps(chart_data),
    })


# Vendor Risk Assessment View
@login_required
def risk_assessment_detail(request, assessment_id):
    assessment = get_object_or_404(RiskAssessment, id=assessment_id)

    if not request.user.is_superuser and assessment.vendor.user != request.user:
        return HttpResponse("Unauthorized access", status=403)

    responses = SecurityChecklist.objects.filter(vendor=assessment.vendor, response__isnull=False)

    SCORE_MAPPING = {"Yes": 0, "No": 10, "Partial": 5, "N/A": 0}
    CATEGORY_WEIGHTS = {
        "Technical": 40, "Compliance": 20, "Legal": 15,
        "General": 15, "Operational": 10,
    }

    category_scores = {cat: 0 for cat in CATEGORY_WEIGHTS}
    category_totals = {cat: 0 for cat in CATEGORY_WEIGHTS}

    for item in responses:
        # Normalize category to handle spaces and case mismatches
        category = (item.category or "").strip().title()

        if not item.category:
            template = SecurityChecklistTemplate.objects.filter(question=item.question).first()
            if template:
                item.category = template.category
                item.save(update_fields=["category"])

        if category not in CATEGORY_WEIGHTS:
            continue

        score = SCORE_MAPPING.get(item.response, 0)
        template = SecurityChecklistTemplate.objects.filter(question=item.question).first()
        if template and template.is_critical:
            score *= 1.5

        category_scores[category] += score
        category_totals[category] += 10

    weighted_scores = {
        c: (category_scores[c] / (category_totals[c] or 1)) * CATEGORY_WEIGHTS[c]
        for c in CATEGORY_WEIGHTS
    }

    chart_data = {
        "labels": list(weighted_scores.keys()),
        "datasets": [{
            "label": "Risk Category Scores",
            "data": list(weighted_scores.values()),
            "backgroundColor": ["#4e73df", "#1cc88a", "#36b9cc", "#f6c23e", "#e74a3b"],
            "borderColor": ["#2e59d9", "#17a673", "#2c9faf", "#dda20a", "#be2617"],
            "borderWidth": 1,
        }]
    }

    return render(request, 'risk_assessment.html', {
        'assessment': assessment,
        'vendor': assessment.vendor,
        'risk_level': assessment.risk_level,
        'risk_score': assessment.total_risk_score,
        'weighted_risk_score': assessment.total_risk_score,
        'chart_data': json.dumps(chart_data),
        'date': assessment.assessment_date,
    })

# Vendor List View
@login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'vendor_list.html', {'user_role': request.user.role, 'vendors': vendors})


# Vendor Onboarding View@login_required
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
            assign_questionnaire_to_vendor(vendor)
            messages.success(request, 'Vendor onboarded successfully and checklist has been assigned.')
            return redirect('home')
    else:
        form = VendorOnboardingForm(instance=vendor, initial={'certified': vendor.certified})

    return render(request, 'onboarding.html', {'user_role': request.user.role, 'form': form, 'user': user})


from django.db.models.functions import Lower
from django.db.models import Q

def assign_questionnaire_to_vendor(vendor):
    questions = SecurityChecklistTemplate.objects.filter(
        category__in=["General", "Legal", "Operational"]
    )

    questions |= SecurityChecklistTemplate.objects.filter(
        category="Technical"
    ).filter(Q(vendor_type=vendor.vendor_type) | Q(vendor_type="Any"))

    selected_cert_names = vendor.certifications.values_list('name', flat=True)
    if selected_cert_names:
        normalized = [cert.strip().lower() for cert in selected_cert_names]

        compliance = SecurityChecklistTemplate.objects.annotate(
            lower_standard=Lower("compliance_standard")
        ).filter(
            category="Compliance",
            standard_required=True,
            lower_standard__in=normalized
        )
        questions |= compliance

    for q in questions.distinct():
        checklist, created = SecurityChecklist.objects.get_or_create(
            vendor=vendor,
            question=q.question,
            defaults={
                "status": "Pending",
                "category": q.category
            }
        )

        # 🛠 Ensure category is correctly set
        if not checklist.category:
            checklist.category = q.category
            checklist.save(update_fields=["category"])


@login_required
def generate_questionnaire(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    # Ensure the vendor belongs to the current logged-in user
    if vendor.user != request.user:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    if request.method == "POST":
        # Log POST data for debugging
        logger.debug(f"POST data for vendor {vendor.id}: {request.POST}")
        
        # Process existing checklist items
        all_items = SecurityChecklist.objects.filter(vendor=vendor)
        saved_items = []
        for item in all_items:
            answer = request.POST.get(f"response_{item.id}")
            if answer is not None:
                item.response = answer
                item.status = "Completed"
                item.save()
                saved_items.append(item.id)
            else:
                logger.warning(f"No response found for checklist item {item.id} (question: {item.question}, category: {item.category})")
        
        # Log any checklist items that weren't saved
        unsaved_items = all_items.exclude(id__in=saved_items)
        if unsaved_items:
            logger.warning(f"Unsaved checklist items for vendor {vendor.id}: {[f'ID:{item.id}, Question:{item.question}, Category:{item.category}' for item in unsaved_items]}")
        
        # Compute risk score and redirect
        compute_risk_score(vendor)
        messages.success(request, "Checklist responses saved successfully.")
        return redirect("home")

    else:  # GET request
        # Fetch questions from various categories
        questions = SecurityChecklistTemplate.objects.filter(
            category__in=["General", "Legal", "Operational"]
        )
        questions |= SecurityChecklistTemplate.objects.filter(
            category="Technical"
        ).filter(Q(vendor_type=vendor.vendor_type) | Q(vendor_type="Any"))

        # Filter compliance questions based on vendor certifications
        def normalize_string(s):
            if not s:
                return ""
            s = s.strip().lower()
            s = re.sub(r'\s+', ' ', s)
            s = re.sub(r'[-_]', ' ', s)
            return s

        selected_cert_names = vendor.certifications.values_list('name', flat=True)
        if selected_cert_names:
            normalized = [normalize_string(cert) for cert in selected_cert_names]
            compliance = SecurityChecklistTemplate.objects.annotate(
                normalized_standard=Lower("compliance_standard")
            ).filter(
                category="Compliance",
                standard_required=True,
                normalized_standard__in=normalized
            )
            # Log unmatched certifications
            all_standards = SecurityChecklistTemplate.objects.filter(category="Compliance", standard_required=True).values_list('compliance_standard', flat=True)
            unmatched = set(normalized) - set(normalize_string(std) for std in all_standards if std)
            if unmatched:
                logger.warning(f"Unmatched certifications for vendor {vendor.name}: {unmatched}")
            questions |= compliance

        # Create or update checklist items without deleting existing ones
        existing_questions = SecurityChecklist.objects.filter(vendor=vendor).values_list('question', flat=True)
        for q in questions.distinct():
            if q.question not in existing_questions:
                checklist, created = SecurityChecklist.objects.get_or_create(
                    vendor=vendor,
                    question=q.question,
                    defaults={
                        "status": "Pending",
                        "category": q.category
                    }
                )
                if not checklist.category:
                    checklist.category = q.category
                    checklist.save(update_fields=["category"])
            else:
                # Update category if needed
                checklist = SecurityChecklist.objects.get(vendor=vendor, question=q.question)
                if checklist.category != q.category:
                    checklist.category = q.category
                    checklist.save(update_fields=["category"])

        # Fetch all checklist items for this vendor
        all_items = SecurityChecklist.objects.filter(vendor=vendor)
        categories = ["General", "Technical", "Legal", "Compliance", "Operational"]

        # Group checklist items by category, excluding Compliance
        checklist_by_category = {
            category: [item for item in all_items if item.category == category]
            for category in categories if category != "Compliance"
        }

        # Group compliance questions by standard
        compliance_items = [item for item in all_items if item.category == "Compliance"]
        compliance_by_standard = {}
        for item in compliance_items:
            template = SecurityChecklistTemplate.objects.filter(question=item.question).first()
            standard = getattr(template, 'compliance_standard', "Uncategorized") if template else "Uncategorized"
            compliance_by_standard.setdefault(standard or "Uncategorized", []).append(item)

        # Log the number of compliance questions
        logger.debug(f"Compliance questions for vendor {vendor.id}: {len(compliance_items)} items")

        return render(request, "questionnaire.html", {
            "checklist_by_category": checklist_by_category,
            "compliance_by_standard": compliance_by_standard,
            "categories": categories
        })

# Other Views
@login_required
def profile(request):
    return render(request, 'profile.html', {'user_role': request.user.role})

@login_required
def alerts(request):
    return render(request, 'alerts.html', {'user_role': request.user.role})

@login_required
def user_settings_view(request):
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

@login_required
def generate_pdf(request, vendor_id):
    
    
    vendor = get_object_or_404(Vendor, id=vendor_id)
    SCORE_MAPPING = {"Yes": 0, "No": 10, "Partial": 5, "N/A": 0}
    CATEGORY_WEIGHTS = {
        "Technical": 40, "Compliance": 20, "Legal": 15,
        "General": 15, "Operational": 10,
    }

    responses = SecurityChecklist.objects.filter(vendor=vendor, response__isnull=False)
    category_scores = {cat: 0 for cat in CATEGORY_WEIGHTS}
    category_totals = {cat: 0 for cat in CATEGORY_WEIGHTS}
    critical_findings = []

    for item in responses:
        category = item.category
        score = SCORE_MAPPING.get(item.response, 0)

        # Check critical
        template = SecurityChecklistTemplate.objects.filter(question=item.question).first()
        if template and template.is_critical:
            score *= 1.5
            critical_findings.append(item)

        if category in category_scores:
            category_scores[category] += score
            category_totals[category] += 10

    weighted_scores = {
        category: (category_scores[category] / (category_totals[category] or 1)) * CATEGORY_WEIGHTS[category]
        for category in CATEGORY_WEIGHTS
    }

    weighted_risk_score = sum(weighted_scores.values())

    if weighted_risk_score <= 20:
        risk_level = "Low"
    elif 20 < weighted_risk_score <= 50:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # Generate Pie Chart
    plt.figure(figsize=(6, 6), tight_layout=True)
    labels = list(weighted_scores.keys())
    sizes = list(weighted_scores.values())
    colors = ['#28a745', '#ffc107', '#dc3545', '#36b9cc', '#6f42c1']

    plt.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=140,
        textprops={'color': 'black', 'fontsize': 10}
    )
    plt.title("Category-wise Risk Distribution", pad=20, fontsize=14)
    plt.gca().set_aspect('equal')

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    logo_path = os.path.join(settings.BASE_DIR, 'vendor_risk', 'static', 'images', 'landscape.png')
    
    with open(logo_path, 'rb') as logo_file:
        logo_base64 = base64.b64encode(logo_file.read()).decode('utf-8')

# Render PDF HTML
    html = render_to_string('risk_assessment_pdf.html', {
    "vendor": vendor,
    "weighted_risk_score": weighted_risk_score,
    "risk_level": risk_level,
    "weighted_scores": weighted_scores,
    "category_weights": CATEGORY_WEIGHTS,
    "responses": responses,
    "critical_findings": critical_findings,
    "chart_image": image_base64,
        "current_date": datetime.now().strftime('%Y-%m-%d'),
    "current_year": datetime.now().year,
    "riskavant_logo_base64": logo_base64,
})

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename={vendor.name}_risk_report.pdf'
    response.write(weasyprint.HTML(string=html).write_pdf())
    return response
