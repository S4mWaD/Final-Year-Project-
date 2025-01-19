from django.core.management.base import BaseCommand
from vendor_risk.models import Vendor, RiskAssessment
from vendor_risk.utils import calculate_risk_score, classify_risk
from datetime import date

class Command(BaseCommand):
    help = "Automatically assess vendor risks based on questionnaire responses"

    def handle(self, *args, **kwargs):
        vendors = Vendor.objects.all()
        for vendor in vendors:
            score = calculate_risk_score(vendor)
            category = classify_risk(score)

            RiskAssessment.objects.create(
                vendor=vendor,
                assessment_date=date.today(),
                risk_score=score,
                compliance_status=category
            )

            self.stdout.write(f"Updated risk assessment for {vendor.name}: {category} ({score})")
