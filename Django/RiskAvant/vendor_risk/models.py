from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

# 🛡️ Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('User', 'User')
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='User')
    organization_name = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:  # Automatically assign role as "Admin" for superusers
            self.role = 'Admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - ({self.role})"

# 🛡️ Vendor Model
class Vendor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="vendor_profile", default=1)
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
    years_in_operation = models.PositiveIntegerField(blank=True, null=True)
    num_clients = models.PositiveIntegerField(blank=True, null=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    certified = models.CharField(max_length=3, choices=[("yes", "Yes"), ("no", "No")], default="no")
    certifications = models.ManyToManyField("Certification", blank=True, related_name="vendors")
    auditable = models.BooleanField(default=False)
    insurance_coverage = models.TextField(blank=True, null=True)
    agreed_to_terms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 🛡️ Certification Model
class Certification(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# 🛡️ Security Profile Model
class SecurityProfile(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name="security_profile")
    encryption = models.BooleanField(default=False)
    mfa = models.BooleanField(default=False)
    rbac = models.BooleanField(default=False)
    penetration_testing = models.BooleanField(default=False)
    
    CLOUD_USAGE_CHOICES = [
        ('Public Cloud', 'Public Cloud'),
        ('Private Cloud', 'Private Cloud'),
        ('Hybrid Cloud', 'Hybrid Cloud'),
        ('No Cloud', 'No Cloud')
    ]
    cloud_usage = models.CharField(max_length=50, choices=CLOUD_USAGE_CHOICES, default='No Cloud')
    certifications = models.ManyToManyField("Certification", blank=True)

    def __str__(self):
        return f"Security Profile for {self.vendor.name}"

# 🛡️ Risk Assessment Model
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

# 🛡️ Onboarding Questionnaire Model
class OnboardingQuestionnaire(models.Model):
    QUESTION_CATEGORIES = [
        ('General', 'General'),
        ('Technical', 'Technical'),
        ('Compliance', 'Compliance'),
        ('Legal', 'Legal'),
        ('Operational', 'Operational')
    ]
    question_text = models.TextField()
    category = models.CharField(max_length=50, choices=QUESTION_CATEGORIES, default='General')
    is_mandatory = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.category}] {self.question_text}"

# 🛡️ Vendor Response Model

class SecurityChecklist(models.Model):
    CATEGORY_CHOICES = [
        ('Cloud Security', 'Cloud Security'),
        ('Network and Infrastructure', 'Network and Infrastructure'),
        ('Cybersecurity', 'Cybersecurity'),
        ('Software Development', 'Software Development'),
        ('Data Center', 'Data Center'),
        ('Other', 'Other'),
        ('Certifications', 'Certifications'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='security_checklists')
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    question = models.TextField()
    response = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 🛡️ Questionnaire Rules Model
class QuestionnaireRules(models.Model):
    vendor_type = models.CharField(max_length=50, choices=Vendor.VENDOR_TYPES)
    requires_certification = models.BooleanField(default=False)
    min_employees = models.PositiveIntegerField(default=0)
    max_employees = models.PositiveIntegerField(default=10000)
    category = models.CharField(max_length=50, choices=OnboardingQuestionnaire.QUESTION_CATEGORIES)

    def __str__(self):
        return f"Rule for {self.vendor_type} - {self.category}"

class QuestionBank(models.Model):
    QUESTION_CATEGORIES = [
        ('General', 'General'),
        ('Technical', 'Technical'),
        ('Compliance', 'Compliance'),
        ('Legal', 'Legal'),
        ('Operational', 'Operational')
    ]
    
    category = models.CharField(max_length=50, choices=QUESTION_CATEGORIES, default='General')
    question_text = models.TextField()
    vendor_type = models.CharField(
        max_length=50,
        choices=Vendor.VENDOR_TYPES,
        blank=True,  # ✅ Allows empty values only for General & Legal
        null=True
    )
    required_certifications = models.ManyToManyField("Certification", blank=True)
    requires_mfa = models.BooleanField(default=False)
    cloud_requirement = models.CharField(
        max_length=50,
        choices=[
            ('Public Cloud', 'Public Cloud'),
            ('Private Cloud', 'Private Cloud'),
            ('Hybrid Cloud', 'Hybrid Cloud'),
            ('No Cloud', 'No Cloud')
        ],
        blank=True,
        null=True
    )
    min_employees = models.PositiveIntegerField(default=0)
    max_employees = models.PositiveIntegerField(default=10000)

    def save(self, *args, **kwargs):
        """ Ensure vendor_type is required for non-General/Legal categories """
        if self.category not in ["General", "Legal"] and not self.vendor_type:
            raise ValueError("Vendor type is required for non-General/Legal questions.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.category}] {self.question_text[:50]}..."


class VendorResponse(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='responses')  
    response = models.CharField(max_length=255, choices=[
        
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Partial', 'Partial'),
        ('N/A', 'N/A')
    ])
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.question.question_text[:50]}"
