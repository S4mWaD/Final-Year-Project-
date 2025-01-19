from django.core.management.base import BaseCommand
from vendor_risk.models import Vendor

class Command(BaseCommand):
    help = "Populate the Vendor table with sample data"

    def handle(self, *args, **kwargs):
        vendor_data = [
            {
                "name": "AWS Cloud Services",
                "vendor_type": "Cloud Service Provider",
                "contact_email": "aws-support@aws.com",
                "contact_phone": "123-456-7890",
                "address": "Seattle, WA, USA",
            },
            {
                "name": "Azure Cloud Solutions",
                "vendor_type": "Cloud Service Provider",
                "contact_email": "support@azure.com",
                "contact_phone": "123-456-7891",
                "address": "Redmond, WA, USA",
            },
            {
                "name": "Google Cloud Platform",
                "vendor_type": "Cloud Service Provider",
                "contact_email": "gcp-support@google.com",
                "contact_phone": "123-456-7892",
                "address": "Mountain View, CA, USA",
            },
            {
                "name": "Microsoft Office Suite",
                "vendor_type": "Software Vendor",
                "contact_email": "office-support@microsoft.com",
                "contact_phone": "123-456-7893",
                "address": "Redmond, WA, USA",
            },
            {
                "name": "Adobe Systems",
                "vendor_type": "Software Vendor",
                "contact_email": "support@adobe.com",
                "contact_phone": "123-456-7894",
                "address": "San Jose, CA, USA",
            },
            {
                "name": "Cisco Networking",
                "vendor_type": "Network Infrastructure",
                "contact_email": "support@cisco.com",
                "contact_phone": "123-456-7895",
                "address": "San Jose, CA, USA",
            },
            {
                "name": "Netgear Solutions",
                "vendor_type": "Network Infrastructure",
                "contact_email": "support@netgear.com",
                "contact_phone": "123-456-7896",
                "address": "San Francisco, CA, USA",
            },
            {
                "name": "Equinix Data Centers",
                "vendor_type": "Data Center",
                "contact_email": "support@equinix.com",
                "contact_phone": "123-456-7897",
                "address": "Sunnyvale, CA, USA",
            },
            {
                "name": "Digital Realty",
                "vendor_type": "Data Center",
                "contact_email": "support@digitalrealty.com",
                "contact_phone": "123-456-7898",
                "address": "Austin, TX, USA",
            },
            {
                "name": "Custom Vendor 1",
                "vendor_type": "Other",
                "contact_email": "support@customvendor1.com",
                "contact_phone": "123-456-7899",
                "address": "New York, NY, USA",
            },
        ]

        for data in vendor_data:
            vendor, created = Vendor.objects.get_or_create(
                name=data["name"],
                vendor_type=data["vendor_type"],
                contact_email=data["contact_email"],
                contact_phone=data["contact_phone"],
                address=data["address"],
            )
            if created:
                self.stdout.write(f"Added Vendor: {vendor.name}")
            else:
                self.stdout.write(f"Vendor {vendor.name} already exists!")

        self.stdout.write("Vendor table population complete.")
