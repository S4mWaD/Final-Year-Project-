import csv
from django.core.management.base import BaseCommand
from vendor_risk.models import SecurityChecklistTemplate

class Command(BaseCommand):
    help = "Import questions from a CSV file into SecurityChecklistTemplate"

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_path = kwargs['csv_path']
        with open(csv_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            imported_count = 0

            for row in reader:
                SecurityChecklistTemplate.objects.create(
                    question=row['question'],
                    category=row['category'],
                    is_critical=row['is_critical'].lower() == 'true',
                    vendor_type=row['vendor_type'],
                    standard_required=row['standard_required'].lower() == 'true',
                    compliance_standard=row.get('compliance_standard') or None
                )
                imported_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {imported_count} questions from {csv_path}'))
