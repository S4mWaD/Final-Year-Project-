from django.core.management.base import BaseCommand
from vendor_risk.models import QuestionBank, Certification

class Command(BaseCommand):
    help = "Populate the QuestionBank with predefined security questionnaire questions"

    def handle(self, *args, **kwargs):
        # Sample Certifications
        iso_27001, _ = Certification.objects.get_or_create(name="ISO 27001")
        soc_2, _ = Certification.objects.get_or_create(name="SOC 2")
        pci_dss, _ = Certification.objects.get_or_create(name="PCI DSS")

        # Define Questions by Category
        questions = [
            {"question_text": "Do you comply with GDPR regulations?", "category": "Compliance", "vendor_type": "Cloud Service Provider", "required_certifications": [iso_27001], "requires_mfa": False, "min_employees": 10, "max_employees": 10000},
            {"question_text": "Have you undergone a SOC 2 compliance audit in the last year?", "category": "Compliance", "vendor_type": "Data Center", "required_certifications": [soc_2], "requires_mfa": False, "min_employees": 50, "max_employees": 5000},
            {"question_text": "Do you adhere to PCI DSS standards for handling payment data?", "category": "Compliance", "vendor_type": "Software Vendor", "required_certifications": [pci_dss], "requires_mfa": True, "min_employees": 100, "max_employees": 10000},
            {"question_text": "Do you have a formal security policy in place?", "category": "Compliance", "vendor_type": "Cloud Service Provider", "required_certifications": [], "requires_mfa": False, "min_employees": 20, "max_employees": 5000},
            {"question_text": "Do you encrypt data at rest and in transit?", "category": "Technical", "vendor_type": "Software Vendor", "required_certifications": [iso_27001], "requires_mfa": True, "min_employees": 10, "max_employees": 5000},
            {"question_text": "Do you conduct regular penetration testing?", "category": "Technical", "vendor_type": "Network Infrastructure", "required_certifications": [soc_2], "requires_mfa": False, "min_employees": 100, "max_employees": 1000},
            {"question_text": "Are employees trained in cybersecurity best practices?", "category": "General", "vendor_type": "Software Vendor", "required_certifications": [], "requires_mfa": False, "min_employees": 1, "max_employees": 10000},
            {"question_text": "Do you enforce multi-factor authentication for all users?", "category": "Technical", "vendor_type": "Cloud Service Provider", "required_certifications": [iso_27001], "requires_mfa": True, "min_employees": 20, "max_employees": 5000},
            {"question_text": "Have you conducted a third-party security audit in the past year?", "category": "Risk Assessment", "vendor_type": "Software Vendor", "required_certifications": [soc_2], "requires_mfa": False, "min_employees": 10, "max_employees": 10000},
            {"question_text": "Do you have a documented incident response plan?", "category": "Operational", "vendor_type": "Network Infrastructure", "required_certifications": [], "requires_mfa": False, "min_employees": 50, "max_employees": 10000},
        ]
        
        # Bulk Insert Questions into the Database
        for q in questions:
            question_obj, created = QuestionBank.objects.get_or_create(
                question_text=q["question_text"],
                category=q["category"],
                vendor_type=q["vendor_type"],  # ✅ FIXED: Assign vendor type correctly
                requires_mfa=q["requires_mfa"],
                min_employees=q["min_employees"],
                max_employees=q["max_employees"]
            )

            # Assign Required Certifications
            for cert in q["required_certifications"]:
                question_obj.required_certifications.add(cert)

            question_obj.save()
            self.stdout.write(self.style.SUCCESS(f"✔ Added Question: {q['question_text']}"))

        self.stdout.write(self.style.SUCCESS("✅ Successfully populated the QuestionBank!"))
