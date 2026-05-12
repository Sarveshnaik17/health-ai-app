"""
MediVision AI - Security Module
Password hashing with bcrypt and JWT token management.
"""

import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from config import Config


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_token(username: str, role: str = "user") -> str:
    """Create a JWT access token with expiration."""
    payload = {
        "sub": username,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    Returns the payload dict or raises jwt.InvalidTokenError.
    """
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])


def get_username_from_token(token: str) -> str:
    """Extract the username from a valid JWT token."""
    payload = decode_token(token)
    return payload["sub"]
