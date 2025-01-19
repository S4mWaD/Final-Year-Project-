from django.core.management.base import BaseCommand
from vendor_risk.models import Questionnaire

class Command(BaseCommand):
    help = "Insert default questionnaire for all vendor types"

    def handle(self, *args, **kwargs):
        vendor_types = [
            'Cloud Service Provider',
            'Software Vendor',
            'Network Infrastructure',
            'Data Center',
            'Other'
        ]

        questions = {
            'Cloud Service Provider': [
                "Do you provide multi-factor authentication?",
                "How do you secure API endpoints?",
                "Is customer data encrypted at rest?",
                "Is customer data encrypted during transit?",
                "Do you have a documented disaster recovery plan?",
                "How often do you conduct security audits?",
                "What compliance certifications do you hold (e.g., ISO 27001)?",
                "Do you offer role-based access control for administrators?",
                "How do you protect against DDoS attacks?",
                "Are audit logs generated and available for customer review?",
                "Do you perform regular penetration testing on your infrastructure?",
                "What is your data backup retention policy?",
                "Are user passwords hashed and salted using secure algorithms?",
                "How do you handle zero-day vulnerabilities in your services?",
                "Do you offer encryption key management to your customers?"
            ],
            'Software Vendor': [
                "How frequently do you release software updates?",
                "Do you conduct static and dynamic code analysis during development?",
                "Are third-party libraries scanned for vulnerabilities before integration?",
                "How do you secure sensitive data stored by your software?",
                "Do you provide secure coding training to your developers?",
                "How is patch management handled for software vulnerabilities?",
                "Are software binaries digitally signed before release?",
                "Do you offer documentation for secure configuration of your software?",
                "How do you protect against common OWASP vulnerabilities (e.g., SQL injection)?",
                "What mechanisms are in place to ensure secure authentication in your software?",
                "Do you provide audit logs for software actions and events?",
                "How do you respond to zero-day vulnerabilities found in your software?",
                "Are your software dependencies managed securely?",
                "Do you have a vulnerability disclosure program for external researchers?",
                "What is your approach to mitigating supply chain attacks in your software?"
            ],
            'Network Infrastructure': [
                "How do you secure network devices (e.g., routers, switches) against unauthorized access?",
                "Do you provide firmware updates for network hardware vulnerabilities?",
                "Are your network devices compliant with industry standards (e.g., IEEE, NIST)?",
                "How is data encrypted during transmission across the network?",
                "Do you implement intrusion detection and prevention systems?",
                "How do you manage firewall rule updates for customers?",
                "Are default passwords disabled on your network devices?",
                "What measures are in place to detect and prevent DDoS attacks?",
                "Do you support VPN connections with secure protocols (e.g., IPsec, OpenVPN)?",
                "How do you handle logging and monitoring of network activities?",
                "Are your network configurations periodically reviewed for security?",
                "How do you mitigate risks associated with BYOD (Bring Your Own Device)?",
                "Do you provide secure access for remote management of network devices?",
                "How do you address vulnerabilities found in your network infrastructure products?",
                "Do you provide detailed documentation on network device configurations?"
            ],
            'Data Center': [
                "What physical security measures are in place to prevent unauthorized access?",
                "Are CCTV cameras installed to monitor sensitive areas of the data center?",
                "How do you enforce access control to data center facilities?",
                "Is there a fire suppression system in place to protect equipment?",
                "Do you have redundant power supplies and backup generators?",
                "Are environmental controls (e.g., temperature, humidity) monitored continuously?",
                "How often are physical security policies reviewed and updated?",
                "Are visitors logged and escorted when accessing the facility?",
                "How do you ensure compliance with standards like SOC 2 or ISO 27001?",
                "Do you have disaster recovery procedures in case of data center failures?",
                "Are data backups stored offsite in a secure location?",
                "How do you protect against insider threats in the data center?",
                "Is your data center compliant with GDPR and other regional regulations?",
                "How do you ensure network segmentation for tenants in a shared data center?",
                "Are server rooms locked and accessible only to authorized personnel?"
            ],
            'Other': [
                "What security policies are in place to protect customer data?",
                "Are employees trained on security best practices?",
                "Do you conduct background checks on employees handling sensitive information?",
                "How do you ensure compliance with GDPR, HIPAA, or other industry regulations?",
                "Is encryption used to protect sensitive customer data?",
                "How do you handle incident response in case of a security breach?",
                "Are access controls implemented to restrict unauthorized system access?",
                "Do you have a documented policy for secure password management?",
                "How do you mitigate risks associated with third-party vendors?",
                "Are periodic audits conducted to ensure compliance with security policies?",
                "What is your process for handling customer complaints related to security?",
                "Do you provide a point of contact for reporting security issues?",
                "How do you monitor and detect unusual activities in your systems?",
                "Are physical security controls in place at your facilities?",
                "How do you manage data disposal when no longer needed?"
            ]
        }

        for vendor_type, question_list in questions.items():
            for question_text in question_list:
                Questionnaire.objects.create(
                    vendor_type=vendor_type,
                    question_text=question_text
                )
                self.stdout.write(f"Inserted question for {vendor_type}: {question_text}")

        self.stdout.write("All questions have been successfully inserted!")
