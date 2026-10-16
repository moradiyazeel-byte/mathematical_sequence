"""
routes/health_routes.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Health Blueprint

Endpoints:
    GET   /api/health            Basic health status check
    GET   /api/health/detailed   Detailed health status check (DB and model)
──────────────────────────────────────────────────────────────────────────────
"""

import logging
from flask import Blueprint, jsonify, current_app
from database.database import get_connection

logger = logging.getLogger("seqpredict.health_routes")

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    """Basic health check indicating that the Flask server is running."""
    return jsonify({"success": True, "status": "UP"}), 200


@health_bp.route("/health/detailed", methods=["GET"])
def health_detailed():
    """
    Detailed health check inspecting database connectivity and ML model loading.
    
    Returns a 200 OK even if degraded, but status is set to "DEGRADED".
    """
    db_status = "UP"
    db_error = None
    try:
        conn = get_connection()
        # Verify connectivity with a simple query
        cur = conn.cursor()
        try:
            cur.execute("SELECT 1")
            cur.fetchone()
        finally:
            cur.close()
    except Exception as exc:
        db_status = "DOWN"
        db_error = str(exc)
        logger.error("Detailed health check database error: %s", exc)

    model_status = "NOT_LOADED"
    model_version = "N/A"
    try:
        model = current_app.extensions.get("model")
        if model is not None:
            model_status = "LOADED"
            model_version = getattr(model, "version", "unknown")
    except Exception as exc:
        logger.error("Detailed health check model inspect error: %s", exc)

    status = "UP"
    if db_status == "DOWN":
        status = "DEGRADED"

    return jsonify({
        "success": True,
        "status": status,
        "database": {
            "status": db_status,
            "error": db_error,
        },
        "model": {
            "status": model_status,
            "version": model_version,
        },
        "system": {
            "app_name": current_app.config.get("APP_NAME", "SeqPredict"),
            "app_version": current_app.config.get("APP_VERSION", "1.0.0"),
        }
    }), 200
