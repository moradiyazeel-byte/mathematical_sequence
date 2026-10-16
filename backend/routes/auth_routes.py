"""
routes/auth_routes.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Authentication Blueprint

Endpoints:
    POST  /api/auth/register    Register a new user account
    POST  /api/auth/login       Authenticate credentials, return JWT access token
──────────────────────────────────────────────────────────────────────────────
"""

import re
import logging
from datetime import datetime, timezone
import jwt
import bcrypt
from flask import Blueprint, request, jsonify, current_app

from database.database import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    update_last_login,
)

logger = logging.getLogger("seqpredict.auth_routes")

auth_bp = Blueprint("auth", __name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

def _ok(data: dict, status: int = 200):
    return jsonify({"success": True, "data": data}), status


def _err(message: str, status: int = 400, code: str = "ERROR"):
    return jsonify({"success": False, "error": message, "error_code": code}), status


def hash_password(password: str, rounds: int) -> str:
    """Hash a password using bcrypt."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds))
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def generate_token(user_id: int, role: str) -> str:
    """Generate a signed JWT access token for a user."""
    secret = current_app.config.get("JWT_SECRET_KEY", "")
    algo = current_app.config.get("JWT_ALGORITHM", "HS256")
    expires_in = current_app.config.get("JWT_ACCESS_EXPIRES")
    
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + expires_in,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, secret, algorithm=algo)


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user account.
    
    Request body (JSON):
        {
            "username": "user123",
            "email": "user@example.com",
            "password": "secretpassword",
            "full_name": "John Doe"  // optional
        }
    """
    if not request.is_json:
        return _err("Request body must be JSON.", 400, "BAD_REQUEST")

    body = request.get_json(silent=True) or {}
    username = (body.get("username") or "").strip()
    email = (body.get("email") or "").strip()
    password = body.get("password")
    full_name = (body.get("full_name") or "").strip() or None

    # Validation
    if not username:
        return _err("Username is required.", 422, "VALIDATION_ERROR")
    if not email:
        return _err("Email address is required.", 422, "VALIDATION_ERROR")
    if not password:
        return _err("Password is required.", 422, "VALIDATION_ERROR")

    # Basic regex validation for email
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return _err("Invalid email format.", 422, "INVALID_EMAIL")

    if len(password) < 6:
        return _err("Password must be at least 6 characters long.", 422, "PASSWORD_TOO_SHORT")

    if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
        return _err("Username can only contain letters, numbers, underscores, and hyphens.", 422, "INVALID_USERNAME")

    try:
        # Hash password using configured bcrypt rounds
        rounds = current_app.config.get("BCRYPT_LOG_ROUNDS", 12)
        password_hash = hash_password(password, rounds)
        
        # Default role is "user"
        user_id = create_user(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role="user",
        )
        
        logger.info("User registered successfully — id=%d username=%s", user_id, username)
        
        return _ok({
            "id": user_id,
            "username": username,
            "email": email,
            "full_name": full_name,
            "role": "user"
        }, 201)

    except ValueError as exc:
        msg = str(exc).lower()
        if "username" in msg:
            return _err("Username is already taken.", 409, "USERNAME_TAKEN")
        if "email" in msg:
            return _err("Email address is already registered.", 409, "EMAIL_TAKEN")
        return _err(f"Registration failed: {exc}", 409, "REGISTRATION_FAILED")
    except Exception as exc:
        logger.error("Registration error: %s", exc, exc_info=True)
        return _err("An unexpected error occurred during registration.", 500, "SERVER_ERROR")


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user credentials and return a JWT token.
    
    Request body (JSON):
        {
            "username": "user123",  // or "email"
            "password": "secretpassword"
        }
    """
    if not request.is_json:
        return _err("Request body must be JSON.", 400, "BAD_REQUEST")

    body = request.get_json(silent=True) or {}
    identity = (body.get("username") or body.get("email") or "").strip()
    password = body.get("password")

    if not identity:
        return _err("Username or email is required.", 422, "VALIDATION_ERROR")
    if not password:
        return _err("Password is required.", 422, "VALIDATION_ERROR")

    # Fetch user details (check email or username)
    user = None
    if "@" in identity:
        user = get_user_by_email(identity)
    if not user:
        user = get_user_by_username(identity)

    # Validate user existence and password
    if not user or not verify_password(password, user["password_hash"]):
        return _err("Invalid username or password.", 401, "INVALID_CREDENTIALS")

    # Check if user is active
    if not user["is_active"]:
        return _err("This account has been deactivated.", 403, "DEACTIVATED_ACCOUNT")

    try:
        # Generate token
        token = generate_token(user["id"], user["role"])
        
        # Update last login timestamp
        update_last_login(user["id"])
        
        logger.info("User logged in successfully — id=%d username=%s", user["id"], user["username"])
        
        return _ok({
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
        }, 200)

    except Exception as exc:
        logger.error("Login error: %s", exc, exc_info=True)
        return _err("An unexpected error occurred during login.", 500, "SERVER_ERROR")
