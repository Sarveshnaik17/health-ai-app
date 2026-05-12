"""
MediVision AI - File Upload Routes
POST /api/upload - Accept CSV for batch prediction
"""
import io, pandas as pd
from flask import Blueprint, request
from utils.helpers import token_required, success_response, error_response
from models.predictor import predictor

upload_bp = Blueprint("upload", __name__, url_prefix="/api")

REQUIRED_COLS = ["Pregnancies","Glucose","BloodPressure","SkinThickness","Insulin","BMI","DiabetesPedigreeFunction","Age"]

@upload_bp.route("/upload", methods=["POST"])
@token_required
def upload_csv(current_user):
    if "file" not in request.files:
        return error_response("No file uploaded", 400)
    file = request.files["file"]
    if not file.filename.endswith(".csv"):
        return error_response("Only CSV files are accepted", 400)
    try:
        content = file.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(content))
    except Exception as e:
        return error_response(f"Failed to parse CSV: {str(e)}", 400)
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        return error_response(f"Missing columns: {', '.join(missing)}", 400)
    results = []
    for _, row in df.iterrows():
        inp = {col: float(row[col]) for col in REQUIRED_COLS}
        try:
            pred = predictor.predict(inp)
            results.append({"input": inp, "risk": pred["risk_label"],
                "probability": pred["probability"], "category": pred["risk_category"]["level"]})
        except Exception as e:
            results.append({"input": inp, "error": str(e)})
    summary = {"total": len(results), "high_risk": sum(1 for r in results if r.get("risk")=="High Risk"),
        "low_risk": sum(1 for r in results if r.get("risk")=="Low Risk"),
        "errors": sum(1 for r in results if "error" in r)}
    return success_response(data={"results": results, "summary": summary})
