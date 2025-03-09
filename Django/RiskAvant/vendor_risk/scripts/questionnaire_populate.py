import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

from vendor_risk.models import Vendor, Questionnaire, VendorResponse

# ✅ 1. Define Vendor Categories
categories = {
    "Cloud Service Provider": Vendor.objects.get_or_create(name="Cloud Service Provider")[0],
    "Software Vendor": Vendor.objects.get_or_create(name="Software Vendor")[0],
    "Network Infrastructure": Vendor.objects.get_or_create(name="Network Infrastructure")[0],
    "Data Center": Vendor.objects.get_or_create(name="Data Center")[0],
}

#  2. Defining Yes/No Questions for Each Category
questions_data = [
    # Security Questions
    ("Do you have a formal Information Security Policy?", "Security", ["Cloud Service Provider", "Software Vendor", "Network Infrastructure", "Data Center"]),
    ("Is Multi-Factor Authentication (MFA) enforced for all users?", "Security", ["Cloud Service Provider", "Software Vendor", "Network Infrastructure", "Data Center"]),
    ("Do you encrypt data at rest?", "Security", ["Cloud Service Provider", "Data Center"]),
    ("Do you encrypt data in transit?", "Security", ["Cloud Service Provider", "Network Infrastructure"]),
    
    # Compliance Questions
    ("Are you ISO 27001 certified?", "Compliance", ["Cloud Service Provider", "Software Vendor", "Network Infrastructure", "Data Center"]),
    ("Are you SOC 2 Type II certified?", "Compliance", ["Cloud Service Provider", "Software Vendor", "Data Center"]),
    ("Do you comply with GDPR or other data privacy laws?", "Compliance", ["Cloud Service Provider", "Software Vendor", "Data Center"]),
    
    # Legal Questions
    ("Do you have legally binding contracts with vendors and suppliers?", "Legal", ["Cloud Service Provider", "Software Vendor", "Network Infrastructure", "Data Center"]),
    ("Do you have a documented Business Continuity Plan?", "Legal", ["Cloud Service Provider", "Software Vendor", "Network Infrastructure", "Data Center"]),

    # Operational Questions
    ("Do you have a dedicated security team?", "Operational", ["Cloud Service Provider", "Software Vendor", "Network Infrastructure", "Data Center"]),
    ("Do you perform background checks on employees?", "Operational", ["Cloud Service Provider", "Software Vendor", "Network Infrastructure", "Data Center"]),
]

# 3. Inserting Questions into the Database
for text, category, vendor_types in questions_data:
    for vendor_type in vendor_types:
        Questionnaire.objects.get_or_create(
            vendor_type=vendor_type, question_text=text, category=category
        )

print(" Successfully populated the questionnaire database!")

#   Define Questionnaire Rules
rules_data = [
    (categories["Cloud Service Provider"], True, 50, 500),
    (categories["Software Vendor"], False, 10, 200),
    (categories["Network Infrastructure"], True, 100, 1000),
]

for category, requires_certification, min_employees, max_employees in rules_data:
    rule = Questionnaire.objects.create(
        category=category,
        requires_certification=requires_certification,
        min_employees=min_employees,
        max_employees=max_employees
    )

    # Assign all questions from that category to the rule
    questions = Questionnaire.objects.filter(vendor_type=category.name)
    rule.question_set.set(questions)

print(" Successfully populated questionnaire rules!")
