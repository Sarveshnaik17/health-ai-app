"""
MediVision AI - Configuration Module
Loads environment variables and provides app-wide settings.
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


class Config:
    """Application configuration loaded from environment variables."""

    MONGO_URI = os.getenv("MONGO_URI")
    JWT_SECRET = os.getenv("JWT_SECRET", "fallback_secret_change_me")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

    # JWT settings
    JWT_EXPIRATION_HOURS = 24

    # Upload settings
    MAX_UPLOAD_SIZE_MB = 10
    ALLOWED_EXTENSIONS = {"csv"}

    # ML settings
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "trained")
    DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "dataset.csv")
