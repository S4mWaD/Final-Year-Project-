from django.db import models
from django.utils.timezone import now

# Core Tables
class Vendor(models.Model):
    name = models.CharField(max_length=255)
    Vendor_Type = [
        ('Cloud Service Provider', 'Cloud Service Provider'), 
        ('Software Vendor', 'Software Vendor'), 
        ('Network Infrastructure', 'Network Infrastructure'), 
        ('Data Center', 'Data Center'), 
        ('Other', 'Other')
    ]
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    vendor_type = models.CharField(max_length=50, choices=Vendor_Type, default='Cloud Service Provider')
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_questions(self):
        return Questionnaire.objects.filter(vendor_type=self.vendor_type)

class Questionnaire(models.Model):
    """
    Stores predefined security-related questions for different vendor types.
    """
    Vendor_Type = [
        ('Cloud Service Provider', 'Cloud Service Provider'), 
        ('Software Vendor', 'Software Vendor'), 
        ('Network Infrastructure', 'Network Infrastructure'), 
        ('Data Center', 'Data Center'), 
        ('Other', 'Other')
    ]
    vendor_type = models.CharField(max_length=50, choices=Vendor_Type)
    question_text = models.TextField()

    def __str__(self):
        return f"{self.vendor_type} - {self.question_text}"

# 🔹 NEW Model: Stores responses to the questionnaire from vendors.
class VendorResponse(models.Model):
    """
    Store vendor responses to security-related questions.
    """
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

class RiskAssessment(models.Model):
    """
    Stores risk assessment details for a vendor.
    Risk score is dynamically computed based on questionnaire responses.
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='risk_assessments')
    assessment_date = models.DateField(default=now)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    compliance_status = models.CharField(max_length=50, choices=[('Compliant', 'Compliant'), ('Non-Compliant', 'Non-Compliant')], default='Non-Compliant')
    recommendations = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.assessment_date}"
