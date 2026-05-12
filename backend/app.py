"""
MediVision AI - Flask API Server
================================
Production-grade REST API with JWT auth, CORS, blueprints.
Run: python app.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from routes.auth import auth_bp
    from routes.predictions import predictions_bp
    from routes.dashboard import dashboard_bp
    from routes.reports import reports_bp
    from routes.upload import upload_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(upload_bp)

    # Health check
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "MediVision AI API"})

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"status": "error", "error": "Internal server error"}), 500

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"status": "error", "error": f"File too large. Max {Config.MAX_UPLOAD_SIZE_MB}MB"}), 413

    # Load ML model at startup
    try:
        from models.predictor import predictor
        predictor.load()
        print("ML model loaded successfully")
    except FileNotFoundError:
        print("WARNING: ML model not found. Run 'python -m models.ml_pipeline' to train.")
    except Exception as e:
        print(f"WARNING: Failed to load ML model: {e}")

    return app

if __name__ == "__main__":
    app = create_app()
    print(f"\n  MediVision AI API running on http://localhost:{Config.FLASK_PORT}\n")
    app.run(host="0.0.0.0", port=Config.FLASK_PORT, debug=Config.FLASK_ENV == "development")
