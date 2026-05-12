"""
MediVision AI - Helper Utilities
Shared utility functions used across the application.
"""

import functools
from flask import request, jsonify
from utils.security import decode_token
import jwt


def token_required(f):
    """
    Decorator that enforces JWT authentication on a Flask route.
    Injects `current_user` (username) as the first argument after self/cls.
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401

        try:
            payload = decode_token(token)
            current_user = payload["sub"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f):
    """
    Decorator that enforces admin role on a Flask route.
    Must be used after @token_required.
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401

        try:
            payload = decode_token(token)
            if payload.get("role") != "admin":
                return jsonify({"error": "Admin access required"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated


def parse_pagination(default_page=1, default_per_page=20):
    """Parse pagination parameters from query string."""
    page = request.args.get("page", default_page, type=int)
    per_page = request.args.get("per_page", default_per_page, type=int)
    per_page = min(per_page, 100)  # Cap at 100
    skip = (page - 1) * per_page
    return page, per_page, skip


def success_response(data=None, message="Success", status=200):
    """Create a standardized success response."""
    response = {"status": "success", "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status


def error_response(message="An error occurred", status=400):
    """Create a standardized error response."""
    return jsonify({"status": "error", "error": message}), status
