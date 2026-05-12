"""
MediVision AI - Prediction Routes
POST /api/predict           — Run single prediction
GET  /api/predictions       — List prediction history (with search/filter/pagination)
GET  /api/predictions/stats — Aggregated prediction stats
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from bson import ObjectId
from utils.db import get_predictions_collection
from utils.helpers import token_required, success_response, error_response, parse_pagination
from models.predictor import predictor

predictions_bp = Blueprint("predictions", __name__, url_prefix="/api")


@predictions_bp.route("/predict", methods=["POST"])
@token_required
def predict(current_user):
    """Run a health risk prediction with the trained ML model."""
    data = request.get_json()

    if not data:
        return error_response("Request body is required", 400)

    # Extract required fields
    required_fields = [
        "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
        "Insulin", "BMI", "DiabetesPedigreeFunction", "Age",
    ]

    input_data = {}
    for field in required_fields:
        value = data.get(field)
        if value is None:
            return error_response(f"Missing required field: {field}", 400)
        try:
            input_data[field] = float(value)
        except (ValueError, TypeError):
            return error_response(f"Invalid value for {field}: must be numeric", 400)

    # Run prediction
    try:
        result = predictor.predict(input_data)
    except FileNotFoundError as e:
        return error_response(str(e), 503)
    except Exception as e:
        return error_response(f"Prediction failed: {str(e)}", 500)

    # Save to MongoDB
    preds = get_predictions_collection()
    record = {
        "user": current_user,
        "input_data": input_data,
        "risk": result["risk_label"],
        "probability": result["probability"],
        "confidence": result["confidence"],
        "risk_category": result["risk_category"]["level"],
        "anomalies_count": len(result["anomalies"]),
        "timestamp": datetime.now(timezone.utc),
    }
    inserted = preds.insert_one(record)
    result["prediction_id"] = str(inserted.inserted_id)

    return success_response(data=result, message="Prediction completed")


@predictions_bp.route("/predictions", methods=["GET"])
@token_required
def get_predictions(current_user):
    """Get paginated prediction history with optional filters."""
    page, per_page, skip = parse_pagination()

    # Filters
    risk_filter = request.args.get("risk")
    search = request.args.get("search", "").strip()

    preds = get_predictions_collection()

    query = {"user": current_user}
    if risk_filter and risk_filter in ["High Risk", "Low Risk"]:
        query["risk"] = risk_filter
    if search:
        query["risk_category"] = {"$regex": search, "$options": "i"}

    total = preds.count_documents(query)
    records = list(
        preds.find(query, {"_id": 1, "risk": 1, "probability": 1, "confidence": 1,
                           "risk_category": 1, "timestamp": 1, "input_data": 1})
        .sort("timestamp", -1)
        .skip(skip)
        .limit(per_page)
    )

    # Serialize ObjectId and datetime
    for r in records:
        r["_id"] = str(r["_id"])
        if "timestamp" in r and hasattr(r["timestamp"], "isoformat"):
            r["timestamp"] = r["timestamp"].isoformat()

    return success_response(data={
        "predictions": records,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    })


@predictions_bp.route("/predictions/stats", methods=["GET"])
@token_required
def get_prediction_stats(current_user):
    """Get aggregated statistics for the user's predictions."""
    preds = get_predictions_collection()

    pipeline = [
        {"$match": {"user": current_user}},
        {
            "$group": {
                "_id": None,
                "total_predictions": {"$sum": 1},
                "high_risk_count": {
                    "$sum": {"$cond": [{"$eq": ["$risk", "High Risk"]}, 1, 0]}
                },
                "low_risk_count": {
                    "$sum": {"$cond": [{"$eq": ["$risk", "Low Risk"]}, 1, 0]}
                },
                "avg_probability": {"$avg": "$probability"},
                "max_probability": {"$max": "$probability"},
                "min_probability": {"$min": "$probability"},
                "avg_confidence": {"$avg": "$confidence"},
            }
        },
    ]

    result = list(preds.aggregate(pipeline))

    if not result:
        stats = {
            "total_predictions": 0,
            "high_risk_count": 0,
            "low_risk_count": 0,
            "avg_probability": 0,
            "max_probability": 0,
            "min_probability": 0,
            "avg_confidence": 0,
            "risk_distribution": [],
            "recent_trend": [],
        }
    else:
        stats = result[0]
        del stats["_id"]

        # Round values
        for key in ["avg_probability", "max_probability", "min_probability", "avg_confidence"]:
            stats[key] = round(stats.get(key, 0), 2)

    # Risk distribution for pie chart
    dist_pipeline = [
        {"$match": {"user": current_user}},
        {"$group": {"_id": "$risk_category", "count": {"$sum": 1}}},
    ]
    stats["risk_distribution"] = [
        {"category": r["_id"], "count": r["count"]}
        for r in preds.aggregate(dist_pipeline)
    ]

    # Recent trend (last 20 predictions)
    recent = list(
        preds.find(
            {"user": current_user},
            {"probability": 1, "timestamp": 1, "risk": 1, "_id": 0},
        )
        .sort("timestamp", -1)
        .limit(20)
    )
    for r in recent:
        if "timestamp" in r and hasattr(r["timestamp"], "isoformat"):
            r["timestamp"] = r["timestamp"].isoformat()
    stats["recent_trend"] = list(reversed(recent))

    return success_response(data=stats)
