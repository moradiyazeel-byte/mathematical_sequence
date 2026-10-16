"""
routes/user_routes.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — User Profile Blueprint

Endpoints:
    GET   /api/user/profile     Retrieve authenticated user details
    PUT   /api/user/profile     Update authenticated user profile fields
──────────────────────────────────────────────────────────────────────────────
"""

import re
import logging
from flask import Blueprint, request, jsonify, current_app, g

from database.database import get_user_by_id, update_user
from utils.auth import require_auth, _ok, _err
from routes.auth_routes import hash_password

logger = logging.getLogger("seqpredict.user_routes")

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
@require_auth
def get_profile():
    """Retrieve profile details of the authenticated user."""
    try:
        user = get_user_by_id(g.user_id)
        if not user:
            return _err("User profile not found.", 404, "NOT_FOUND")

        return _ok({
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "is_active": bool(user["is_active"]),
            "created_at": user["created_at"],
            "last_login_at": user["last_login_at"]
        })
    except Exception as exc:
        logger.error("Error retrieving user profile: %s", exc, exc_info=True)
        return _err("An unexpected error occurred retrieving profile.", 500, "SERVER_ERROR")


@user_bp.route("/profile", methods=["PUT"])
@require_auth
def update_profile():
    """
    Update authenticated user profile.
    
    Request body (JSON):
        {
            "full_name": "Jane Doe",      // optional
            "email": "jane@example.com",  // optional
            "password": "newpassword"     // optional
        }
    """
    if not request.is_json:
        return _err("Request body must be JSON.", 400, "BAD_REQUEST")

    body = request.get_json(silent=True) or {}
    
    fields = {}
    if "full_name" in body:
        fields["full_name"] = (body["full_name"] or "").strip() or None
        
    if "email" in body:
        email = (body["email"] or "").strip()
        if not email:
            return _err("Email address cannot be empty.", 422, "VALIDATION_ERROR")
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            return _err("Invalid email format.", 422, "INVALID_EMAIL")
        fields["email"] = email

    if "password" in body:
        password = body["password"]
        if not password or len(password) < 6:
            return _err("Password must be at least 6 characters long.", 422, "PASSWORD_TOO_SHORT")
        
        rounds = current_app.config.get("BCRYPT_LOG_ROUNDS", 12)
        fields["password_hash"] = hash_password(password, rounds)

    if not fields:
        return _err("No fields provided for update.", 422, "NO_UPDATES")

    try:
        updated = update_user(g.user_id, **fields)
        if not updated:
            return _err("Failed to update user profile.", 500, "UPDATE_FAILED")

        # Refetch fresh details
        user = get_user_by_id(g.user_id)
        logger.info("User profile updated successfully — id=%d", g.user_id)

        return _ok({
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "is_active": bool(user["is_active"]),
            "created_at": user["created_at"],
            "last_login_at": user["last_login_at"]
        })

    except ValueError as exc:
        msg = str(exc).lower()
        if "email" in msg:
            return _err("Email address is already registered.", 409, "EMAIL_TAKEN")
        if "username" in msg:
            return _err("Username is already taken.", 409, "USERNAME_TAKEN")
        return _err(f"Profile update failed: {exc}", 400, "UPDATE_FAILED")
    except Exception as exc:
        logger.error("Error updating user profile: %s", exc, exc_info=True)
        return _err("An unexpected error occurred updating profile.", 500, "SERVER_ERROR")
