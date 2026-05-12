"""
MediVision AI - Prediction Service
====================================
Loads the trained ensemble model and provides:
  - Single-patient prediction with confidence scores
  - SHAP-like feature contribution explanation
  - Risk categorization (Low / Moderate / High / Critical)
  - Anomaly detection (inputs outside training distribution)
  - Batch prediction from DataFrames
"""

import os
import json
import numpy as np
import pandas as pd
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINED_DIR = os.path.join(BASE_DIR, "trained")

# Feature names matching the training pipeline
RAW_FEATURE_NAMES = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age",
]

ZERO_INVALID_COLS = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]

# Training-set medians for imputation (fallback values from Pima dataset)
TRAINING_MEDIANS = {
    "Glucose": 117.0,
    "BloodPressure": 72.0,
    "SkinThickness": 29.0,
    "Insulin": 125.0,
    "BMI": 32.0,
}

# Approximate training-set statistics for anomaly detection
TRAINING_RANGES = {
    "Pregnancies": (0, 17),
    "Glucose": (44, 199),
    "BloodPressure": (24, 122),
    "SkinThickness": (7, 99),
    "Insulin": (14, 846),
    "BMI": (18.2, 67.1),
    "DiabetesPedigreeFunction": (0.078, 2.42),
    "Age": (21, 81),
}


class Predictor:
    """Enterprise prediction service with explainability."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.metadata = None
        self._loaded = False

    def load(self):
        """Load model, scaler, and metadata from trained/ directory."""
        model_path = os.path.join(TRAINED_DIR, "model.joblib")
        scaler_path = os.path.join(TRAINED_DIR, "scaler.joblib")
        meta_path = os.path.join(TRAINED_DIR, "metadata.json")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Trained model not found at {model_path}. "
                "Run 'python -m models.ml_pipeline' first."
            )

        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

        with open(meta_path, "r") as f:
            self.metadata = json.load(f)

        self._loaded = True
        return self

    def _ensure_loaded(self):
        if not self._loaded:
            self.load()

    def _preprocess_input(self, input_data: dict) -> np.ndarray:
        """
        Preprocess a single patient's input data.
        Matches the training pipeline: zero-replacement, imputation, feature engineering.
        """
        # Create DataFrame with raw features
        df = pd.DataFrame([input_data])

        # Replace impossible zeros with medians
        for col in ZERO_INVALID_COLS:
            if col in df.columns and df[col].iloc[0] == 0:
                df[col] = TRAINING_MEDIANS.get(col, 0)

        # Feature engineering (must match training)
        df["Glucose_BMI"] = df["Glucose"] * df["BMI"]
        df["Age_Pregnancies"] = df["Age"] * df["Pregnancies"]
        df["Insulin_Glucose_Ratio"] = df["Insulin"] / (df["Glucose"] + 1e-6)
        df["BMI_Age"] = df["BMI"] * df["Age"]
        df["HighGlucose"] = (df["Glucose"] >= 140).astype(int)
        df["HighBMI"] = (df["BMI"] >= 30).astype(int)

        # Order columns to match training
        feature_names = self.metadata["feature_names"]
        X = df[feature_names].values

        # Scale
        X_scaled = self.scaler.transform(X)
        return X_scaled

    def _detect_anomalies(self, input_data: dict) -> list:
        """Check if input values fall outside training data ranges."""
        anomalies = []
        for feature, (low, high) in TRAINING_RANGES.items():
            value = input_data.get(feature, 0)
            if value < low or value > high:
                anomalies.append({
                    "feature": feature,
                    "value": value,
                    "expected_range": [low, high],
                    "severity": "warning" if abs(value - (low + high) / 2) < (high - low) else "critical",
                })
        return anomalies

    def _get_risk_category(self, probability: float) -> dict:
        """Categorize risk level based on prediction probability."""
        if probability < 0.25:
            return {"level": "Low", "color": "#22c55e", "description": "Low risk. Maintain healthy lifestyle."}
        elif probability < 0.50:
            return {"level": "Moderate", "color": "#eab308", "description": "Moderate risk. Consider lifestyle changes and regular check-ups."}
        elif probability < 0.75:
            return {"level": "High", "color": "#f97316", "description": "High risk. Consult a healthcare professional promptly."}
        else:
            return {"level": "Critical", "color": "#ef4444", "description": "Critical risk. Seek immediate medical attention."}

    def _get_feature_contributions(self, input_data: dict) -> list:
        """
        Approximate feature contributions using feature importance + input magnitude.
        (Lightweight alternative to full SHAP for fast API responses.)
        """
        self._ensure_loaded()
        importance = self.metadata.get("feature_importance", {})
        raw_features = self.metadata.get("raw_feature_names", RAW_FEATURE_NAMES)

        contributions = []
        for feature in raw_features:
            imp = importance.get(feature, 0)
            value = input_data.get(feature, 0)
            contributions.append({
                "feature": feature,
                "value": value,
                "importance": round(imp, 4),
            })

        # Sort by importance descending
        contributions.sort(key=lambda x: x["importance"], reverse=True)
        return contributions

    def predict(self, input_data: dict) -> dict:
        """
        Run prediction on a single patient's data.

        Args:
            input_data: Dict with keys matching RAW_FEATURE_NAMES

        Returns:
            Dict with prediction, probability, risk category, explanation, anomalies.
        """
        self._ensure_loaded()

        # Preprocess
        X_scaled = self._preprocess_input(input_data)

        # Predict
        prediction = int(self.model.predict(X_scaled)[0])
        probabilities = self.model.predict_proba(X_scaled)[0]
        risk_probability = float(probabilities[1])
        confidence = float(max(probabilities)) * 100

        # Risk category
        risk_category = self._get_risk_category(risk_probability)

        # Feature contributions
        contributions = self._get_feature_contributions(input_data)

        # Anomaly detection
        anomalies = self._detect_anomalies(input_data)

        # Health recommendations based on inputs
        recommendations = self._generate_recommendations(input_data, risk_probability)

        return {
            "prediction": prediction,
            "risk_label": "High Risk" if prediction == 1 else "Low Risk",
            "probability": round(risk_probability * 100, 2),
            "confidence": round(confidence, 2),
            "risk_category": risk_category,
            "feature_contributions": contributions,
            "anomalies": anomalies,
            "recommendations": recommendations,
            "model_info": {
                "type": self.metadata.get("model_type", "Ensemble"),
                "accuracy": self.metadata.get("metrics", {}).get("accuracy", 0),
                "f1_score": self.metadata.get("metrics", {}).get("f1_score", 0),
            },
        }

    def predict_batch(self, data_list: list) -> list:
        """Run predictions on multiple patients."""
        return [self.predict(d) for d in data_list]

    def _generate_recommendations(self, input_data: dict, probability: float) -> list:
        """Generate personalized health recommendations based on input values."""
        recs = []

        glucose = input_data.get("Glucose", 0)
        bmi = input_data.get("BMI", 0)
        bp = input_data.get("BloodPressure", 0)
        age = input_data.get("Age", 0)
        insulin = input_data.get("Insulin", 0)

        if glucose > 140:
            recs.append({
                "icon": "🔬",
                "title": "High Glucose Detected",
                "detail": f"Your glucose level ({glucose} mg/dL) is above normal. Consider dietary changes and consult an endocrinologist.",
                "priority": "high",
            })

        if bmi > 30:
            recs.append({
                "icon": "⚖️",
                "title": "Elevated BMI",
                "detail": f"BMI of {bmi} indicates obesity. Regular exercise and a balanced diet are recommended.",
                "priority": "medium",
            })

        if bp > 90:
            recs.append({
                "icon": "❤️",
                "title": "Blood Pressure Monitoring",
                "detail": f"Blood pressure of {bp} mmHg is elevated. Monitor regularly and reduce sodium intake.",
                "priority": "medium",
            })

        if insulin > 200:
            recs.append({
                "icon": "💉",
                "title": "High Insulin Levels",
                "detail": f"Insulin level of {insulin} μU/mL is high. This may indicate insulin resistance.",
                "priority": "high",
            })

        if age > 45:
            recs.append({
                "icon": "📅",
                "title": "Age-Related Screening",
                "detail": "Regular diabetes screening is recommended for individuals over 45.",
                "priority": "low",
            })

        if probability < 0.3:
            recs.append({
                "icon": "✅",
                "title": "Maintain Current Lifestyle",
                "detail": "Your risk is currently low. Continue regular exercise and healthy eating.",
                "priority": "low",
            })

        return recs

    def get_model_metrics(self) -> dict:
        """Return stored model evaluation metrics."""
        self._ensure_loaded()
        return {
            "metrics": self.metadata.get("metrics", {}),
            "cv_metrics": self.metadata.get("cv_metrics", {}),
            "feature_importance": self.metadata.get("feature_importance", {}),
            "model_type": self.metadata.get("model_type", "Unknown"),
            "trained_at": self.metadata.get("trained_at", "Unknown"),
            "dataset_size": self.metadata.get("dataset_size", 0),
        }


# Global singleton
predictor = Predictor()
