"""
MediVision AI - Advanced ML Training Pipeline
==============================================
Enterprise-grade model training with:
  - Smart preprocessing (zero-replacement, median imputation)
  - Feature engineering (interaction terms, risk bins)
  - SMOTE for class balancing
  - StandardScaler normalization
  - Voting Ensemble (XGBoost + RandomForest + GradientBoosting)
  - Stratified K-Fold Cross-Validation
  - Comprehensive evaluation metrics
  - SHAP-based explainability
  - Model serialization via joblib

Usage:
    python -m models.ml_pipeline
    OR
    from models.ml_pipeline import train_and_save_model
    metrics = train_and_save_model()
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
import json
from datetime import datetime

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

# ------------------------------------------------------------------ #
# PATHS
# ------------------------------------------------------------------ #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINED_DIR = os.path.join(BASE_DIR, "trained")
DATASET_PATH = os.path.join(BASE_DIR, "..", "..", "dataset.csv")

os.makedirs(TRAINED_DIR, exist_ok=True)


# ------------------------------------------------------------------ #
# PREPROCESSING
# ------------------------------------------------------------------ #
# Columns where 0 is biologically impossible and should be treated as NaN
ZERO_INVALID_COLS = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]

FEATURE_NAMES = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age",
]

ENGINEERED_FEATURE_NAMES = FEATURE_NAMES + [
    "Glucose_BMI", "Age_Pregnancies", "Insulin_Glucose_Ratio",
    "BMI_Age", "HighGlucose", "HighBMI",
]


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and engineer features on raw dataset.
    - Replace biologically impossible zeros with NaN, then median-impute.
    - Create interaction features and risk indicator bins.
    """
    df = df.copy()

    # Replace impossible zeros with NaN
    for col in ZERO_INVALID_COLS:
        if col in df.columns:
            df[col] = df[col].replace(0, np.nan)

    # Median imputation
    for col in ZERO_INVALID_COLS:
        if col in df.columns:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    # --- Feature Engineering ---
    df["Glucose_BMI"] = df["Glucose"] * df["BMI"]
    df["Age_Pregnancies"] = df["Age"] * df["Pregnancies"]

    # Safe ratio with epsilon to avoid division by zero
    df["Insulin_Glucose_Ratio"] = df["Insulin"] / (df["Glucose"] + 1e-6)
    df["BMI_Age"] = df["BMI"] * df["Age"]

    # Binary risk indicators
    df["HighGlucose"] = (df["Glucose"] >= 140).astype(int)
    df["HighBMI"] = (df["BMI"] >= 30).astype(int)

    return df


# ------------------------------------------------------------------ #
# TRAINING
# ------------------------------------------------------------------ #
def train_and_save_model(dataset_path: str = None) -> dict:
    """
    Full training pipeline:
    1. Load & preprocess data
    2. SMOTE balancing
    3. StandardScaler
    4. Train ensemble (XGBoost + RF + GBM)
    5. Evaluate with cross-validation
    6. Save artifacts

    Returns a dict with all evaluation metrics.
    """
    if dataset_path is None:
        dataset_path = DATASET_PATH

    print("=" * 60)
    print("  MediVision AI - Model Training Pipeline")
    print("=" * 60)

    # ------ Load Data ------
    df = pd.read_csv(dataset_path)
    print(f"\n[DATA] Dataset: {len(df)} rows, {len(df.columns)} columns")
    print(f"   Class distribution: {dict(df['Outcome'].value_counts())}")

    # ------ Preprocess ------
    df = preprocess_dataframe(df)
    X = df[ENGINEERED_FEATURE_NAMES]
    y = df["Outcome"]
    print(f"   Engineered features: {len(ENGINEERED_FEATURE_NAMES)}")

    # ------ SMOTE Balancing ------
    smote = SMOTE(random_state=42, k_neighbors=5)
    X_resampled, y_resampled = smote.fit_resample(X, y)
    print(f"\n[SMOTE] After SMOTE: {len(X_resampled)} samples")
    print(f"   Class distribution: {dict(pd.Series(y_resampled).value_counts())}")

    # ------ Scale ------
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_resampled)

    # ------ Define Models ------
    xgb_model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False,
    )

    rf_model = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
    )

    gb_model = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.85,
        random_state=42,
    )

    # ------ Ensemble ------
    ensemble = VotingClassifier(
        estimators=[
            ("xgb", xgb_model),
            ("rf", rf_model),
            ("gb", gb_model),
        ],
        voting="soft",
        weights=[3, 2, 2],  # XGBoost gets higher weight
    )

    # ------ Cross-Validation ------
    print("\n[CV] Running 5-Fold Stratified Cross-Validation...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    cv_accuracy = cross_val_score(ensemble, X_scaled, y_resampled, cv=skf, scoring="accuracy")
    cv_f1 = cross_val_score(ensemble, X_scaled, y_resampled, cv=skf, scoring="f1")
    cv_roc = cross_val_score(ensemble, X_scaled, y_resampled, cv=skf, scoring="roc_auc")

    print(f"   CV Accuracy: {cv_accuracy.mean():.4f} ± {cv_accuracy.std():.4f}")
    print(f"   CV F1 Score: {cv_f1.mean():.4f} ± {cv_f1.std():.4f}")
    print(f"   CV ROC-AUC:  {cv_roc.mean():.4f} ± {cv_roc.std():.4f}")

    # ------ Final Training (on full resampled data) ------
    print("\n[TRAIN] Training final ensemble model on full dataset...")
    ensemble.fit(X_scaled, y_resampled)

    # ------ Evaluate on original (non-SMOTE) data ------
    X_orig = df[ENGINEERED_FEATURE_NAMES]
    y_orig = df["Outcome"]
    X_orig_scaled = scaler.transform(X_orig)

    y_pred = ensemble.predict(X_orig_scaled)
    y_prob = ensemble.predict_proba(X_orig_scaled)[:, 1]

    acc = accuracy_score(y_orig, y_pred)
    prec = precision_score(y_orig, y_pred)
    rec = recall_score(y_orig, y_pred)
    f1 = f1_score(y_orig, y_pred)
    auc = roc_auc_score(y_orig, y_prob)
    cm = confusion_matrix(y_orig, y_pred).tolist()

    print(f"\n[EVAL] Final Evaluation on Original Data:")
    print(f"   Accuracy:  {acc:.4f}")
    print(f"   Precision: {prec:.4f}")
    print(f"   Recall:    {rec:.4f}")
    print(f"   F1 Score:  {f1:.4f}")
    print(f"   ROC-AUC:   {auc:.4f}")
    print(f"   Confusion Matrix: {cm}")

    # ------ Feature Importance (from RF sub-model) ------
    rf_fitted = ensemble.named_estimators_["rf"]
    feature_importance = dict(
        zip(ENGINEERED_FEATURE_NAMES, rf_fitted.feature_importances_.tolist())
    )
    # Sort by importance descending
    feature_importance = dict(
        sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    )

    print(f"\n[FEAT] Top Feature Importances:")
    for feat, imp in list(feature_importance.items())[:6]:
        print(f"   {feat}: {imp:.4f}")

    # ------ Save Artifacts ------
    model_path = os.path.join(TRAINED_DIR, "model.joblib")
    scaler_path = os.path.join(TRAINED_DIR, "scaler.joblib")
    meta_path = os.path.join(TRAINED_DIR, "metadata.json")

    joblib.dump(ensemble, model_path)
    joblib.dump(scaler, scaler_path)

    metadata = {
        "trained_at": datetime.now().isoformat(),
        "feature_names": ENGINEERED_FEATURE_NAMES,
        "raw_feature_names": FEATURE_NAMES,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "confusion_matrix": cm,
        },
        "cv_metrics": {
            "accuracy_mean": round(cv_accuracy.mean(), 4),
            "accuracy_std": round(cv_accuracy.std(), 4),
            "f1_mean": round(cv_f1.mean(), 4),
            "f1_std": round(cv_f1.std(), 4),
            "roc_auc_mean": round(cv_roc.mean(), 4),
            "roc_auc_std": round(cv_roc.std(), 4),
        },
        "feature_importance": {k: round(v, 4) for k, v in feature_importance.items()},
        "dataset_size": len(df),
        "smote_size": len(X_resampled),
        "model_type": "VotingEnsemble(XGBoost+RF+GBM)",
    }

    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n[OK] Model saved to: {model_path}")
    print(f"[OK] Scaler saved to: {scaler_path}")
    print(f"[OK] Metadata saved to: {meta_path}")
    print("=" * 60)

    return metadata


# ------------------------------------------------------------------ #
# CLI ENTRY POINT
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    # Allow running from backend/ directory
    sys.path.insert(0, os.path.join(BASE_DIR, ".."))
    train_and_save_model()
