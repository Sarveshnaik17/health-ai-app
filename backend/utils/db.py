"""
MediVision AI - Database Module
MongoDB connection and collection accessors.
"""

from pymongo import MongoClient
from config import Config

# Singleton connection
_client = None
_db = None


def get_client():
    """Get or create MongoDB client singleton."""
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGO_URI)
    return _client


def get_db():
    """Get the healthdb database instance."""
    global _db
    if _db is None:
        _db = get_client()["healthdb"]
    return _db


def get_users_collection():
    """Get the users collection."""
    return get_db()["users"]


def get_predictions_collection():
    """Get the predictions collection."""
    return get_db()["predictions"]


def get_feedback_collection():
    """Get the feedback collection."""
    return get_db()["feedback"]


def get_notifications_collection():
    """Get the notifications collection."""
    return get_db()["notifications"]
