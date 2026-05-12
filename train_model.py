import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load Dataset
df = pd.read_csv("dataset.csv")

# Features / Target
X = df.drop("Outcome", axis=1)
y = df["Outcome"]

# Split Data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

# Model
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Test Accuracy
pred = model.predict(X_test)
acc = accuracy_score(y_test, pred)

print("Model Accuracy:", round(acc * 100, 2), "%")

# Save Model
pickle.dump(model, open("model.pkl", "wb"))

print("model.pkl created successfully")