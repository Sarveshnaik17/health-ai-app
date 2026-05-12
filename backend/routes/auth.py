"""
MediVision AI - Authentication Routes
POST /api/auth/register  — Create new account
POST /api/auth/login     — Login and receive JWT
GET  /api/auth/profile   — Get user profile (protected)
PUT  /api/auth/profile   — Update profile settings (protected)
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from utils.db import get_users_collection
from utils.security import hash_password, verify_password, create_token
from utils.helpers import token_required, success_response, error_response

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user account."""
    data = request.get_json()

    if not data:
        return error_response("Request body is required", 400)

    username = data.get("username", "").strip()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()

    # Validation
    if not username or len(username) < 3:
        return error_response("Username must be at least 3 characters", 400)
    if not password or len(password) < 6:
        return error_response("Password must be at least 6 characters", 400)

    users = get_users_collection()

    # Check if username already exists
    if users.find_one({"username": username}):
        return error_response("Username already exists", 409)

    # Create user with hashed password
    user_doc = {
        "username": username,
        "password": hash_password(password),
        "full_name": full_name or username,
        "role": "user",
        "created_at": datetime.now(timezone.utc),
        "settings": {
            "theme": "dark",
            "notifications": True,
            "email_reports": False,
        },
        "avatar_color": f"#{hash(username) % 0xFFFFFF:06x}",
    }
    users.insert_one(user_doc)

    # Return token immediately so user is logged in after registration
    token = create_token(username, "user")

    return success_response(
        data={
            "token": token,
            "user": {
                "username": username,
                "full_name": user_doc["full_name"],
                "role": "user",
            },
        },
        message="Registration successful",
        status=201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    data = request.get_json()

    if not data:
        return error_response("Request body is required", 400)

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return error_response("Username and password are required", 400)

    users = get_users_collection()
    user = users.find_one({"username": username})

    if not user:
        return error_response("Invalid username or password", 401)

    # Support both legacy plain-text and bcrypt passwords
    stored_password = user["password"]
    if stored_password.startswith("$2"):
        # bcrypt hash
        if not verify_password(password, stored_password):
            return error_response("Invalid username or password", 401)
    else:
        # Legacy plain-text password — verify and upgrade to bcrypt
        if password != stored_password:
            return error_response("Invalid username or password", 401)
        # Upgrade to bcrypt
        users.update_one(
            {"_id": user["_id"]},
            {"$set": {"password": hash_password(password)}},
        )

    role = user.get("role", "user")
    token = create_token(username, role)

    return success_response(
        data={
            "token": token,
            "user": {
                "username": username,
                "full_name": user.get("full_name", username),
                "role": role,
                "settings": user.get("settings", {}),
            },
        },
        message="Login successful",
    )


@auth_bp.route("/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    """Get the current user's profile."""
    users = get_users_collection()
    user = users.find_one({"username": current_user}, {"password": 0, "_id": 0})

    if not user:
        return error_response("User not found", 404)

    # Convert datetime to string
    if "created_at" in user and hasattr(user["created_at"], "isoformat"):
        user["created_at"] = user["created_at"].isoformat()

    return success_response(data=user)


@auth_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile(current_user):
    """Update user profile settings."""
    data = request.get_json()

    if not data:
        return error_response("Request body is required", 400)

    users = get_users_collection()

    update_fields = {}
    if "full_name" in data:
        update_fields["full_name"] = data["full_name"].strip()
    if "settings" in data:
        update_fields["settings"] = data["settings"]

    if not update_fields:
        return error_response("No valid fields to update", 400)

    users.update_one({"username": current_user}, {"$set": update_fields})

    return success_response(message="Profile updated successfully")
