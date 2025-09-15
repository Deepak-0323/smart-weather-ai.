import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import numpy as np

# 1. Create a simple dataset
data = {
    'MinTemp': [10, 15, 18, 20, 22, 8, 12, 16, 21, 23],
    'MaxTemp': [20, 25, 28, 30, 32, 15, 22, 26, 31, 33],
    'Humidity3pm': [60, 75, 80, 70, 85, 90, 70, 65, 55, 78],
    'Pressure3pm': [1015, 1012, 1010, 1013, 1008, 1005, 1014, 1011, 1009, 1010],
    'RainTomorrow': ['No', 'Yes', 'Yes', 'No', 'Yes', 'Yes', 'No', 'No', 'No', 'Yes']
}
df = pd.DataFrame(data)

# 2. Preprocess and train
X = df[['MinTemp', 'MaxTemp', 'Humidity3pm', 'Pressure3pm']]
y = df['RainTomorrow'].map({'Yes': 1, 'No': 0})
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 3. Save the model
joblib.dump(model, 'rainfall_model.pkl')
print("Model saved as rainfall_model.pkl")

# Save a dummy scaler to prevent errors in app.py
joblib.dump(None, 'scaler.pkl')
print("Dummy scaler saved as scaler.pkl")