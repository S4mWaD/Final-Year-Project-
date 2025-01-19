import pandas as pd
import random

# Features relevant for risk assessment based on the questionnaire
features = [
    "Access_Control", "CCTV_Monitoring", "Physical_Security",
    "Network_Documentation", "Secure_Protocols", "OWASP_Vulnerabilities",
    "Data_Encrypted_Transit", "Third_Party_Risks", "Periodic_Audits",
    "Intrusion_Detection", "DDoS_Prevention", "Compliance_Standards",
    "Secure_API_Endpoints", "Multi_Factor_Auth", "Disaster_Recovery"
]

#  Data for risk assessment
num_samples = 500  # Number of samples
data = []

for _ in range(num_samples):
    # binary responses (Yes = 1, No = 0) for each feature
    responses = [random.randint(0, 1) for _ in features]
    
    # Assigning a risk category based on patterns (low, medium, high)
    # For simplicity, creating a weighted pattern: more "Yes" answers -> lower risk
    yes_count = sum(responses)
    if yes_count > 10:
        risk_category = 0  # Low Risk
    elif yes_count > 5:
        risk_category = 1  # Medium Risk
    else:
        risk_category = 2  # High Risk
    
    data.append(responses + [risk_category])

# DataFrame
columns = features + ["Risk_Category"]
df = pd.DataFrame(data, columns=columns)

# Saving the synthetic data to a CSV file
df.to_csv("test_data.csv", index=False)

print("Synthetic data saved to 'test_data.csv'")
