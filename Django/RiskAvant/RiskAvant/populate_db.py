import random
from faker import Faker
from datetime import datetime, timedelta
from vendor_risk.models import Vendor, RiskAssessment, SecurityChecklist, StandardsCompliance, User, RiskCategory, VendorDocument, AuditLog, Alert, DashboardMetric

fake = Faker()

# Creating Users
def create_users(n=5):
    users = []
    for _ in range(n):
        user = User.objects.create(
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
            role=random.choice(["Admin", "User"])
        )
        users.append(user)
    return users

# Creating Vendors
def create_vendors(n=10):
    vendors = []
    for _ in range(n):
        vendor = Vendor.objects.create(
            name=fake.company(),
            industry=fake.word(),
            contact_email=fake.company_email(),
            contact_phone=fake.phone_number(),
            address=fake.address()
        )
        vendors.append(vendor)
    return vendors

# Creating Risk Assessments
def create_risk_assessments(vendors):
    assessments = []
    for vendor in vendors:
        assessment = RiskAssessment.objects.create(
            vendor=vendor,
            assessment_date=fake.date_this_decade(),
            risk_score=round(random.uniform(1.0, 10.0), 2),
            compliance_status=random.choice(["Compliant", "Non-Compliant"]),
            recommendations=fake.text()
        )
        assessments.append(assessment)
    return assessments

# Creating Security Checklists
def create_security_checklists(vendors, n=5):
    questions = [
        "Does the vendor follow ISO 27001 standards?",
        "Does the vendor perform regular security audits?",
        "Does the vendor have a data protection policy?",
        "Are vendor employees trained in security awareness?",
        "Has the vendor faced any data breaches in the past?"
    ]
    
    checklists = []
    for vendor in vendors:
        for _ in range(n):
            checklist = SecurityChecklist.objects.create(
                vendor=vendor,
                question=random.choice(questions),
                response=random.choice(["Yes", "No", "N/A"]),
                status=random.choice(["Pending", "Completed"])
            )
            checklists.append(checklist)
    return checklists

# Creating Standards Compliance Records
def create_standards_compliance(vendors):
    standards = ["ISO 27001", "NIST CSF", "GDPR", "SOC 2", "PCI DSS"]
    compliance_records = []
    for vendor in vendors:
        record = StandardsCompliance.objects.create(
            vendor=vendor,
            standard=random.choice(standards),
            compliance_status=random.choice(["Compliant", "Non-Compliant", "Partial"]),
            assessment_date=fake.date_this_decade()
        )
        compliance_records.append(record)
    return compliance_records

# Creating Risk Categories
def create_risk_categories():
    categories = ["Financial Risk", "Operational Risk", "Compliance Risk", "Strategic Risk"]
    risk_categories = []
    for category in categories:
        risk_cat = RiskCategory.objects.create(
            category_name=category,
            description=fake.text()
        )
        risk_categories.append(risk_cat)
    return risk_categories

# Creating Vendor Documents
def create_vendor_documents(vendors, n=2):
    documents = []
    doc_types = ["Contract", "Audit Report", "Security Policy"]
    for vendor in vendors:
        for _ in range(n):
            document = VendorDocument.objects.create(
                vendor=vendor,
                document_name=fake.file_name(),
                document_type=random.choice(doc_types),
                file_url=fake.url()
            )
            documents.append(document)
    return documents

# Creating Audit Logs
def create_audit_logs(users, n=10):
    actions = ["User Login", "Vendor Added", "Risk Assessment Updated", "Checklist Reviewed"]
    logs = []
    for _ in range(n):
        log = AuditLog.objects.create(
            user=random.choice(users),
            action=random.choice(actions),
            timestamp=fake.date_time_this_year(),
            details=fake.text()
        )
        logs.append(log)
    return logs

# Creating Alerts
def create_alerts(vendors, n=3):
    alerts = []
    messages = ["Compliance issue detected", "High-risk vendor identified", "Security checklist incomplete"]
    for vendor in vendors:
        for _ in range(n):
            alert = Alert.objects.create(
                vendor=vendor,
                alert_message=random.choice(messages),
                status=random.choice(["Unread", "Read"])
            )
            alerts.append(alert)
    return alerts

# Creating Dashboard Metrics
def create_dashboard_metrics():
    metrics = [
        {"metric_name": "Total Vendors", "value": 100},
        {"metric_name": "High Risk Vendors", "value": 15},
        {"metric_name": "Completed Checklists", "value": 80},
        {"metric_name": "Pending Assessments", "value": 20}
    ]
    dashboard_metrics = []
    for metric in metrics:
        db_metric = DashboardMetric.objects.create(
            metric_name=metric["metric_name"],
            value=metric["value"]
        )
        dashboard_metrics.append(db_metric)
    return dashboard_metrics


# Run Data Population
def populate_database():
    print("Creating Users...")
    users = create_users()
    
    print("Creating Vendors...")
    vendors = create_vendors()
    
    print("Creating Risk Assessments...")
    create_risk_assessments(vendors)
    
    print("Creating Security Checklists...")
    create_security_checklists(vendors)
    
    print("Creating Standards Compliance...")
    create_standards_compliance(vendors)
    
    print("Creating Risk Categories...")
    create_risk_categories()
    
    print("Creating Vendor Documents...")
    create_vendor_documents(vendors)
    
    print("Creating Audit Logs...")
    create_audit_logs(users)
    
    print("Creating Alerts...")
    create_alerts(vendors)
    
    print("Creating Dashboard Metrics...")
    create_dashboard_metrics()
    
    print("Database population complete!")

# Run the script
if __name__ == "__main__":
    populate_database()
