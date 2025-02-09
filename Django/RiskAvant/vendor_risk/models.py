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

    def __str__(self):
        return self.username


# 🔹 Vendor Model
class Vendor(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    vendor_type = models.CharField(max_length=50, choices=VENDOR_TYPES)
    question_text = models.TextField()

    def __str__(self):
        return f"{self.vendor_type} - {self.question_text}"


# 🔹 Vendor Response Model
class VendorResponse(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='responses')
    response = models.CharField(max_length=255, choices=[
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Partial', 'Partial')
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
