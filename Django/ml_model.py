import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Loading the initial test data
data = pd.read_csv('test_data.csv')

# Splitting into features and target
x = data.drop(columns=['Risk_Category'])
y = data['Risk_Category']

# Testing and Training Sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

print(x_train)
[print(y_train)]
# Training the model
model = RandomForestClassifier(random_state=42)
model.fit(x_train, y_train)

# Evaluating the model
y_pred = model.predict(x_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Saving the model
joblib.dump(model, 'model.joblib')
print("Model saved")