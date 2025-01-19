from vendor_risk.models import Vendor, VendorResponse, RiskAssessment
from datetime import date

def calculate_risk_score(vendor):
    """
    Computes the risk score based on vendor responses to the security questionnaire.
    """
    total_score = 0
    responses = VendorResponse.objects.filter(vendor=vendor)

    for response in responses:
        if response.response == 'Yes':
            total_score += 0  # No risk
        elif response.response == 'Partial':
            total_score += 5  # Medium risk
        elif response.response == 'No':
            total_score += 10  # High risk

    # Normalize risk score
    max_score = len(responses) * 10 if responses else 100  # Prevent division by zero
    risk_percentage = (total_score / max_score) * 100

    return min(100, risk_percentage)  # Ensure risk score does not exceed 100

def classify_risk(risk_score):
    """
    Categorizes vendors into risk levels based on computed risk score.
    """
    if risk_score <= 30:
        return "Low Risk"
    elif risk_score <= 60:
        return "Moderate Risk"
    else:
        return "High Risk"
