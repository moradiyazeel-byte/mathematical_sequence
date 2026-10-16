"""
utils/auth.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Authentication & Authorization Utilities

Decorators and helpers for verifying JWT tokens and roles.
──────────────────────────────────────────────────────────────────────────────
"""

from functools import wraps
import jwt
from flask import request, jsonify, current_app, g


def _ok(data: dict, status: int = 200):
    return jsonify({"success": True, "data": data}), status


def _err(message: str, status: int = 400, code: str = "ERROR"):
    return jsonify({"success": False, "error": message, "error_code": code}), status


def _extract_token() -> str | None:
    """Pull Bearer token from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return None


def _verify_token(token: str) -> dict | None:
    """
    Decode and verify JWT. Returns the payload dict on success, None on failure.
    """
    try:
        secret = current_app.config.get("JWT_SECRET_KEY", "")
        algo = current_app.config.get("JWT_ALGORITHM", "HS256")
        payload = jwt.decode(token, secret, algorithms=[algo])
        return payload
    except Exception:
        return None


def optional_auth(f):
    """
    Decorator that attaches user_id and role to g if a valid JWT is present,
    but does NOT reject the request if no token is provided.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if token:
            payload = _verify_token(token)
            if payload:
                g.user_id = payload.get("user_id")
                g.user_role = payload.get("role")
        return f(*args, **kwargs)
    return decorated


def require_auth(f):
    """
    Decorator that rejects requests without a valid JWT with 401.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return _err("Authentication required.", 401, "UNAUTHORISED")
        payload = _verify_token(token)
        if not payload:
            return _err("Invalid or expired token.", 401, "INVALID_TOKEN")
        g.user_id = payload.get("user_id")
        g.user_role = payload.get("role")
        return f(*args, **kwargs)
    return decorated


def require_role(required_role: str):
    """
    Decorator that rejects requests if the user doesn't have the required role.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = _extract_token()
            if not token:
                return _err("Authentication required.", 401, "UNAUTHORISED")
            payload = _verify_token(token)
            if not payload:
                return _err("Invalid or expired token.", 401, "INVALID_TOKEN")
            
            user_role = payload.get("role")
            if user_role != required_role:
                return _err("You do not have permission to access this resource.", 403, "FORBIDDEN")
                
            g.user_id = payload.get("user_id")
            g.user_role = user_role
            return f(*args, **kwargs)
        return decorated
    return decorator
