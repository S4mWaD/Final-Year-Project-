from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

# 🔹 Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('User', 'User')
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='User')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} - ({self.role})"

# 🔹 Vendor Model
class Vendor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="vendor_profile", blank=True, null=True)
    VENDOR_TYPES = [
        ('Cloud Service Provider', 'Cloud Service Provider'), 
        ('Software Vendor', 'Software Vendor'), 
        ('Network Infrastructure', 'Network Infrastructure'), 
        ('Data Center', 'Data Center'), 
        ('Other', 'Other')
    ]
    name = models.CharField(max_length=255)
    vendor_type = models.CharField(max_length=50, choices=VENDOR_TYPES, default='Cloud Service Provider')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    website = models.URLField(blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    business_license = models.CharField(max_length=50, blank=True, null=True)
    years_in_operation = models.IntegerField(blank=True, null=True)
    num_employees = models.CharField(max_length=20, choices=[
        ('1-10', '1-10'), ('11-50', '11-50'), ('51-200', '51-200'),
        ('201-500', '201-500'), ('501+', '501+')
    ], blank=True, null=True)
    num_clients = models.IntegerField(blank=True, null=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    certifications = models.TextField(blank=True, null=True)
    certified = models.BooleanField(default=False)
    auditable = models.BooleanField(default=False)
    insurance_coverage = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    def get_questions(self):
        return Questionnaire.objects.filter(vendor_type=self.vendor_type)

# 🔹 Security Questionnaire Model
class Questionnaire(models.Model):
    VENDOR_TYPES = [
        ('Cloud Service Provider', 'Cloud Service Provider'), 
        ('Software Vendor', 'Software Vendor'), 
        ('Network Infrastructure', 'Network Infrastructure'), 
        ('Data Center', 'Data Center'), 
        ('Other', 'Other')
    ]
    QUESTION_CATEGORIES = [
        ('Security', 'Security'),
        ('Compliance', 'Compliance'),
        ('Legal', 'Legal'),
        ('Operational', 'Operational')
    ]
    vendor_type = models.CharField(max_length=50, choices=VENDOR_TYPES)
    question_text = models.TextField()
    category = models.CharField(max_length=50, choices=QUESTION_CATEGORIES, default='Security')
    is_mandatory = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.vendor_type} - {self.question_text}"

# 🔹 Vendor Response Model
class VendorResponse(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='responses')
    response = models.CharField(max_length=255, choices=[
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Partial', 'Partial'),
        ('N/A', 'N/A')
    ])
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.question.question_text[:50]}"

# 🔹 Risk Assessment Model
class RiskAssessment(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='risk_assessments')
    assessment_date = models.DateField(default=now)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    compliance_status = models.CharField(max_length=50, choices=[('Compliant', 'Compliant'), ('Non-Compliant', 'Non-Compliant')], default='Non-Compliant')
    recommendations = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.assessment_date}"

# 🔹 Onboarding Questionnaire Model
class OnboardingQuestionnaire(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='onboarding_questions')
    question_text = models.TextField()
    is_mandatory = models.BooleanField(default=True)
    response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.vendor.name} - Onboarding Question"
