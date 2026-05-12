"""
MediVision AI - Dashboard Routes
GET /api/dashboard/overview   — Dashboard overview data
GET /api/dashboard/insights   — Auto-generated insights
GET /api/dashboard/model      — Model performance metrics
"""

from flask import Blueprint, request
from datetime import datetime, timezone, timedelta
from utils.db import get_predictions_collection, get_users_collection
from utils.helpers import token_required, success_response, error_response
from models.predictor import predictor

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/overview", methods=["GET"])
@token_required
def overview(current_user):
    """Get comprehensive dashboard overview."""
    preds = get_predictions_collection()
    users = get_users_collection()

    user = users.find_one({"username": current_user}, {"_id": 0, "password": 0})
    user_predictions = list(preds.find({"user": current_user}).sort("timestamp", -1))

    total = len(user_predictions)
    high_risk = sum(1 for p in user_predictions if p.get("risk") == "High Risk")
    low_risk = total - high_risk

    # Calculate average probability
    avg_prob = 0
    if total > 0:
        avg_prob = round(
            sum(p.get("probability", 0) for p in user_predictions) / total, 2
        )

    # Recent activity (last 5 predictions)
    recent_activity = []
    for p in user_predictions[:5]:
        recent_activity.append({
            "id": str(p["_id"]),
            "risk": p.get("risk", "Unknown"),
            "probability": p.get("probability", 0),
            "risk_category": p.get("risk_category", "Unknown"),
            "timestamp": p["timestamp"].isoformat() if hasattr(p.get("timestamp"), "isoformat") else str(p.get("timestamp", "")),
        })

    # Weekly trend
    now = datetime.now(timezone.utc)
    weekly_data = []
    for i in range(7):
        day = now - timedelta(days=6 - i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)

        day_preds = [
            p for p in user_predictions
            if hasattr(p.get("timestamp"), "date") and day_start <= p["timestamp"].replace(tzinfo=timezone.utc if p["timestamp"].tzinfo is None else p["timestamp"].tzinfo) <= day_end
        ]
        weekly_data.append({
            "day": day.strftime("%a"),
            "date": day.strftime("%Y-%m-%d"),
            "count": len(day_preds),
            "avg_risk": round(sum(p.get("probability", 0) for p in day_preds) / max(len(day_preds), 1), 1),
        })

    return success_response(data={
        "user": {
            "username": current_user,
            "full_name": user.get("full_name", current_user) if user else current_user,
            "member_since": user.get("created_at", "").isoformat() if user and hasattr(user.get("created_at"), "isoformat") else "",
        },
        "stats": {
            "total_predictions": total,
            "high_risk_count": high_risk,
            "low_risk_count": low_risk,
            "avg_probability": avg_prob,
        },
        "recent_activity": recent_activity,
        "weekly_trend": weekly_data,
    })


@dashboard_bp.route("/insights", methods=["GET"])
@token_required
def insights(current_user):
    """Generate auto-insights from user's prediction history."""
    preds = get_predictions_collection()
    user_predictions = list(preds.find({"user": current_user}).sort("timestamp", -1))

    total = len(user_predictions)
    insights_list = []

    if total == 0:
        insights_list.append({
            "type": "info",
            "icon": "📊",
            "title": "No Data Yet",
            "description": "Complete your first health prediction to start getting personalized insights.",
        })
        return success_response(data={"insights": insights_list})

    # Insight 1: Risk trend
    high_risk_count = sum(1 for p in user_predictions if p.get("risk") == "High Risk")
    high_risk_pct = round(high_risk_count / total * 100, 1)

    if high_risk_pct > 50:
        insights_list.append({
            "type": "warning",
            "icon": "⚠️",
            "title": "Elevated Risk Pattern",
            "description": f"{high_risk_pct}% of your assessments show high risk. Consider consulting a healthcare professional.",
        })
    elif high_risk_pct < 20:
        insights_list.append({
            "type": "success",
            "icon": "✅",
            "title": "Healthy Trend",
            "description": f"Only {high_risk_pct}% of your assessments are high risk. Great job maintaining your health!",
        })

    # Insight 2: Average risk
    avg_prob = sum(p.get("probability", 0) for p in user_predictions) / total
    if avg_prob > 60:
        insights_list.append({
            "type": "warning",
            "icon": "📈",
            "title": "High Average Risk Score",
            "description": f"Your average risk score is {avg_prob:.1f}%. Regular monitoring is recommended.",
        })
    else:
        insights_list.append({
            "type": "success",
            "icon": "💚",
            "title": "Good Average Score",
            "description": f"Your average risk score is {avg_prob:.1f}%, which is within a healthy range.",
        })

    # Insight 3: Activity frequency
    if total >= 10:
        insights_list.append({
            "type": "info",
            "icon": "🏆",
            "title": "Active Health Monitoring",
            "description": f"You've completed {total} assessments. Consistent monitoring helps track health changes.",
        })

    # Insight 4: Recent trend direction
    if total >= 3:
        recent_3 = user_predictions[:3]
        older_3 = user_predictions[3:6] if total >= 6 else user_predictions[3:]
        if older_3:
            recent_avg = sum(p.get("probability", 0) for p in recent_3) / len(recent_3)
            older_avg = sum(p.get("probability", 0) for p in older_3) / len(older_3)
            if recent_avg < older_avg - 5:
                insights_list.append({
                    "type": "success",
                    "icon": "📉",
                    "title": "Improving Trend",
                    "description": "Your recent risk scores are trending downward. Keep it up!",
                })
            elif recent_avg > older_avg + 5:
                insights_list.append({
                    "type": "warning",
                    "icon": "📈",
                    "title": "Increasing Risk Trend",
                    "description": "Your recent risk scores are trending upward. Consider lifestyle adjustments.",
                })

    return success_response(data={"insights": insights_list})


@dashboard_bp.route("/model", methods=["GET"])
@token_required
def model_metrics(current_user):
    """Get model performance metrics and feature importance."""
    try:
        metrics = predictor.get_model_metrics()
        return success_response(data=metrics)
    except FileNotFoundError:
        return error_response("Model not trained yet", 503)
    except Exception as e:
        return error_response(f"Failed to load model metrics: {str(e)}", 500)
