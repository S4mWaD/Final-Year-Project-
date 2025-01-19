from django.core.management.base import BaseCommand
from vendor_risk.models import Vendor, Questionnaire, VendorResponse
import random

class Command(BaseCommand):
    help = "Populate the VendorResponse table with sample data for testing"

    def handle(self, *args, **kwargs):
        vendors = Vendor.objects.all()
        responses = ['Yes', 'No', 'Partial']

        if not vendors.exists():
            self.stdout.write("No vendors found! Please populate the Vendor table first.")
            return

        for vendor in vendors:
            questions = Questionnaire.objects.filter(vendor_type=vendor.vendor_type)
            if not questions.exists():
                self.stdout.write(f"No questions found for vendor type: {vendor.vendor_type}")
                continue

            for question in questions:
                response = random.choice(responses)  # Randomly choose Yes, No, or Partial
                VendorResponse.objects.create(
                    vendor=vendor,
                    question=question,
                    response=response
                )
                self.stdout.write(f"Added response for vendor {vendor.name}: {response} to question: {question.question_text[:50]}")

        self.stdout.write("VendorResponse table population complete.")
