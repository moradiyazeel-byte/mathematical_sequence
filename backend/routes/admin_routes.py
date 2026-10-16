"""
routes/admin_routes.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Administration Blueprint

Endpoints:
    GET   /api/admin/stats               Get aggregated system statistics
    GET   /api/admin/users               List all system users (paginated)
    POST  /api/admin/users/<id>/status   Enable or disable a user account
    GET   /api/admin/logs                List system event logs (paginated, filtered)
    GET   /api/admin/settings            List all active system settings
    PUT   /api/admin/settings            Create or update a system setting
    GET   /api/admin/model-logs          List machine learning model logs
──────────────────────────────────────────────────────────────────────────────
"""

import logging
from flask import Blueprint, request, jsonify, g

from database.database import (
    get_admin_stats,
    list_users,
    set_user_status,
    get_system_logs,
    list_settings,
    set_setting,
    list_model_logs,
)
from utils.auth import require_role, _ok, _err

logger = logging.getLogger("seqpredict.admin_routes")

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/stats", methods=["GET"])
@require_role("admin")
def stats():
    """Retrieve overview statistics for the administrative dashboard."""
    try:
        data = get_admin_stats()
        return _ok(data)
    except Exception as exc:
        logger.error("Admin stats error: %s", exc, exc_info=True)
        return _err("Failed to retrieve system statistics.", 500, "SERVER_ERROR")


@admin_bp.route("/users", methods=["GET"])
@require_role("admin")
def users():
    """Retrieve a paginated list of registered users."""
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 20, type=int)
        
        # Guard limits
        page = max(page, 1)
        limit = min(max(limit, 1), 100)

        data = list_users(page=page, limit=limit)
        return _ok(data)
    except Exception as exc:
        logger.error("Admin users list error: %s", exc, exc_info=True)
        return _err("Failed to list users.", 500, "SERVER_ERROR")


@admin_bp.route("/users/<int:user_id>/status", methods=["POST"])
@require_role("admin")
def user_status(user_id: int):
    """
    Toggle a user's active status (enable/disable account).
    
    Request body (JSON):
        {
            "is_active": false
        }
    """
    if not request.is_json:
        return _err("Request body must be JSON.", 400, "BAD_REQUEST")

    body = request.get_json(silent=True) or {}
    is_active = body.get("is_active")

    if is_active is None:
        return _err("Missing required parameter: 'is_active' (boolean).", 422, "VALIDATION_ERROR")
    if not isinstance(is_active, bool):
        return _err("'is_active' must be a boolean value.", 422, "VALIDATION_ERROR")

    # Prevent admin from disabling their own account
    if user_id == g.user_id:
        return _err("You cannot modify your own active status.", 400, "SELF_MODIFICATION_PROHIBITED")

    try:
        success = set_user_status(user_id, is_active)
        if not success:
            return _err("User not found.", 404, "NOT_FOUND")

        action = "enabled" if is_active else "disabled"
        logger.info("Admin user action — user #%d was %s by admin #%d", user_id, action, g.user_id)
        
        return _ok({
            "message": f"User status updated successfully to {action}.",
            "user_id": user_id,
            "is_active": is_active
        })
    except Exception as exc:
        logger.error("Admin update user status error: %s", exc, exc_info=True)
        return _err("Failed to update user status.", 500, "SERVER_ERROR")


@admin_bp.route("/logs", methods=["GET"])
@require_role("admin")
def logs():
    """
    Retrieve system event logs.
    
    Query Parameters:
        level (str): Filter by level ("INFO", "WARNING", "ERROR")
        source (str): Filter by source module
        page (int): Page number (default 1)
        limit (int): Logs per page (default 50, max 200)
    """
    try:
        level = request.args.get("level", None)
        source = request.args.get("source", None)
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 50, type=int)

        page = max(page, 1)
        limit = min(max(limit, 1), 200)

        data = get_system_logs(level=level, source=source, page=page, limit=limit)
        return _ok(data)
    except Exception as exc:
        logger.error("Admin system logs error: %s", exc, exc_info=True)
        return _err("Failed to retrieve system logs.", 500, "SERVER_ERROR")


@admin_bp.route("/settings", methods=["GET"])
@require_role("admin")
def settings():
    """Retrieve a list of all active system settings."""
    try:
        data = list_settings()
        return _ok(data)
    except Exception as exc:
        logger.error("Admin list settings error: %s", exc, exc_info=True)
        return _err("Failed to retrieve system settings.", 500, "SERVER_ERROR")


@admin_bp.route("/settings", methods=["PUT"])
@require_role("admin")
def update_setting():
    """
    Create or update a system setting.
    
    Request body (JSON):
        {
            "setting_key": "ml_fallback_enabled",
            "setting_value": false
        }
    """
    if not request.is_json:
        return _err("Request body must be JSON.", 400, "BAD_REQUEST")

    body = request.get_json(silent=True) or {}
    key = (body.get("setting_key") or "").strip()
    value = body.get("setting_value")

    if not key:
        return _err("Missing required parameter: 'setting_key'.", 422, "VALIDATION_ERROR")
    if value is None:
        return _err("Missing required parameter: 'setting_value'.", 422, "VALIDATION_ERROR")

    try:
        success = set_setting(key, value, updated_by=g.user_id)
        if not success:
            return _err("Failed to update setting.", 500, "UPDATE_FAILED")

        logger.info("Admin setting updated — key='%s' updated_by=%d", key, g.user_id)
        return _ok({
            "message": "Setting updated successfully.",
            "setting_key": key,
            "setting_value": value
        })
    except Exception as exc:
        logger.error("Admin update setting error: %s", exc, exc_info=True)
        return _err("Failed to update setting.", 500, "SERVER_ERROR")


@admin_bp.route("/model-logs", methods=["GET"])
@require_role("admin")
def model_logs():
    """
    Retrieve machine learning model training history run logs.
    
    Query Parameters:
        limit (int): Number of history logs to return (default 20, max 100)
    """
    try:
        limit = request.args.get("limit", 20, type=int)
        limit = min(max(limit, 1), 100)

        data = list_model_logs(limit=limit)
        return _ok(data)
    except Exception as exc:
        logger.error("Admin model logs error: %s", exc, exc_info=True)
        return _err("Failed to retrieve model logs.", 500, "SERVER_ERROR")
