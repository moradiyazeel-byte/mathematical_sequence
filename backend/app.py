"""
app.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Flask Application Entry Point

Responsibilities:
  • Create and configure the Flask application (factory pattern)
  • Register all route blueprints (predict, history, auth, user, admin, health)
  • Enable CORS for the frontend origin
  • Initialise the SQLite database (tables created if absent)
  • Load the ML model into memory at startup (singleton via model_loader)
  • Attach request/response lifecycle hooks (logging, timing, error handling)
  • Expose a unified JSON error format for all HTTP exceptions
  • Provide a CLI entry point for development and production

Run (development):
    python app.py

Run (production via gunicorn):
    gunicorn -w 2 -b 0.0.0.0:5000 "app:create_app()"
──────────────────────────────────────────────────────────────────────────────
"""

import os
import time
import logging
import traceback
from datetime import datetime, timezone

from flask import Flask, jsonify, g, request
from flask_cors import CORS

from config import config_map, DevelopmentConfig


# ─────────────────────────────────────────────────────────────────────────────
# Logging setup (module-level so it is active before create_app runs)
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s  [%(levelname)s]  %(name)s — %(message)s",
    datefmt= "%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("seqpredict")


# ─────────────────────────────────────────────────────────────────────────────
# Application factory
# ─────────────────────────────────────────────────────────────────────────────

def create_app(env: str | None = None) -> Flask:
    """
    Create and return a configured Flask application instance.

    Parameters
    ----------
    env : str | None
        Configuration environment name: "development", "production", or
        "testing".  Falls back to the FLASK_ENV environment variable, then
        to "development".

    Returns
    -------
    Flask
        Fully initialised application ready to serve requests.
    """

    # ── Resolve configuration ────────────────────────────────────────────────
    env = env or os.getenv("FLASK_ENV", "development")
    cfg = config_map.get(env, DevelopmentConfig)

    # ── Instantiate Flask ────────────────────────────────────────────────────
    app = Flask(
        __name__,
        static_folder  = None,   # frontend is served separately
        template_folder= None,
    )
    app.config.from_object(cfg)

    logger.info("Starting SeqPredict — env=%s | debug=%s", env, app.config.get("DEBUG"))

    # ── CORS ─────────────────────────────────────────────────────────────────
    _init_cors(app)

    # ── Database ─────────────────────────────────────────────────────────────
    _init_database(app)

    # ── ML model (loaded once, held in app context) ──────────────────────────
    _init_model(app)

    # ── Blueprints ───────────────────────────────────────────────────────────
    _register_blueprints(app)

    # ── Lifecycle hooks ──────────────────────────────────────────────────────
    _register_hooks(app)

    # ── Error handlers ───────────────────────────────────────────────────────
    _register_error_handlers(app)

    # ── Index routes ─────────────────────────────────────────────────────────
    _register_index_routes(app)

    return app


# ─────────────────────────────────────────────────────────────────────────────
# Initialisation helpers
# ─────────────────────────────────────────────────────────────────────────────

def _init_cors(app: Flask) -> None:
    """Enable Cross-Origin Resource Sharing for the configured frontend origin."""

    origins = app.config.get("CORS_ORIGINS", "*")
    CORS(
        app,
        resources     = {r"/api/*": {"origins": origins}},
        supports_credentials = False,
        max_age       = 86_400,       # 24 h preflight cache
    )
    logger.info("CORS enabled — origins: %s", origins)


def _init_database(app: Flask) -> None:
    """
    Ensure the SQLite database file and all tables exist.

    Imports are deferred so that database.py can itself import
    app.config safely at module level once the app is created.
    """
    with app.app_context():
        try:
            from database.database import init_db
            init_db()
            logger.info("Database initialised — %s", app.config.get("DATABASE_PATH"))
        except Exception as exc:
            logger.error("Database initialisation failed: %s", exc)
            # Not fatal — allow startup so health endpoint can report the issue


def _init_model(app: Flask) -> None:
    """
    Load the trained ML model into memory at startup.

    The model is attached to app.extensions["model"] so that any part
    of the application can retrieve it without reloading from disk.
    """
    with app.app_context():
        try:
            from services.model_loader import ModelLoader
            loader = ModelLoader(model_path=app.config.get("MODEL_PATH"))
            loader.load()
            app.extensions["model"] = loader
            logger.info(
                "ML model loaded — version=%s  path=%s",
                loader.version,
                app.config.get("MODEL_PATH"),
            )
        except FileNotFoundError:
            # Model .pkl does not exist yet (pre-training state). The system
            # will still serve rule-based predictions; ML fallback will be
            # disabled until training/train_model.py is run.
            app.extensions["model"] = None
            logger.warning(
                "Model file not found at '%s'. "
                "Run training/train_model.py to generate it. "
                "Rule-based predictions will still work.",
                app.config.get("MODEL_PATH"),
            )
        except Exception as exc:
            app.extensions["model"] = None
            logger.error("Model loading error: %s\n%s", exc, traceback.format_exc())


def _register_blueprints(app: Flask) -> None:
    """Import and register all route blueprints under the /api prefix."""

    from routes.predict_routes import predict_bp
    from routes.history_routes import history_bp
    from routes.auth_routes    import auth_bp
    from routes.user_routes    import user_bp
    from routes.admin_routes   import admin_bp
    from routes.health_routes  import health_bp

    blueprints = [
        (predict_bp, "/api"),
        (history_bp, "/api"),
        (auth_bp,    "/api/auth"),
        (user_bp,    "/api/user"),
        (admin_bp,   "/api/admin"),
        (health_bp,  "/api"),
    ]

    for bp, url_prefix in blueprints:
        app.register_blueprint(bp, url_prefix=url_prefix)
        logger.info("Blueprint registered — /%s  prefix=%s", bp.name, url_prefix)


# ─────────────────────────────────────────────────────────────────────────────
# Lifecycle hooks
# ─────────────────────────────────────────────────────────────────────────────

def _register_hooks(app: Flask) -> None:
    """Attach before/after request hooks for timing, logging, and DB logging."""

    @app.before_request
    def _start_timer() -> None:
        """Record request start time so latency can be included in logs."""
        g.start_time = time.perf_counter()

    @app.after_request
    def _log_request(response):
        """
        Log every completed request with method, path, status, and latency.
        Also write a system_logs record for non-health API calls.
        """
        latency_ms = round((time.perf_counter() - g.get("start_time", time.perf_counter())) * 1000)

        logger.info(
            "%s %s  →  %s  (%dms)",
            request.method,
            request.path,
            response.status_code,
            latency_ms,
        )

        # Persist API requests to system_logs (skip health checks to reduce noise)
        if request.path.startswith("/api") and not request.path.startswith("/api/health"):
            try:
                from database.database import log_system_event
                log_system_event(
                    log_level      = "INFO",
                    source         = "app",
                    message        = f"{request.method} {request.path} → {response.status_code}",
                    endpoint       = request.path,
                    request_method = request.method,
                    status_code    = response.status_code,
                    ip_address     = _get_client_ip(),
                )
            except Exception:
                pass  # Never let logging break the response

        # Attach timing header (useful for frontend debugging)
        response.headers["X-Response-Time-Ms"] = str(latency_ms)
        response.headers["X-Powered-By"]       = "SeqPredict/1.0"

        return response

    @app.teardown_appcontext
    def _close_db_connection(exc=None) -> None:
        """Return the SQLite connection to the connection pool (or close it)."""
        try:
            from database.database import close_connection
            close_connection()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Error handlers — unified JSON responses for all HTTP error codes
# ─────────────────────────────────────────────────────────────────────────────

def _register_error_handlers(app: Flask) -> None:

    def _error_response(status: int, message: str, code: str = None):
        payload = {"success": False, "error": message}
        if code:
            payload["error_code"] = code
        resp = jsonify(payload)
        resp.status_code = status
        return resp

    @app.errorhandler(400)
    def bad_request(e):
        return _error_response(400, str(e.description) or "Bad request", "BAD_REQUEST")

    @app.errorhandler(401)
    def unauthorised(e):
        return _error_response(401, "Authentication required. Please log in.", "UNAUTHORISED")

    @app.errorhandler(403)
    def forbidden(e):
        return _error_response(403, "You do not have permission to access this resource.", "FORBIDDEN")

    @app.errorhandler(404)
    def not_found(e):
        return _error_response(404, f"The requested resource was not found: {request.path}", "NOT_FOUND")

    @app.errorhandler(405)
    def method_not_allowed(e):
        return _error_response(
            405,
            f"Method {request.method} is not allowed for {request.path}.",
            "METHOD_NOT_ALLOWED",
        )

    @app.errorhandler(409)
    def conflict(e):
        return _error_response(409, str(e.description) or "Resource conflict.", "CONFLICT")

    @app.errorhandler(422)
    def unprocessable(e):
        return _error_response(422, str(e.description) or "Unprocessable input.", "UNPROCESSABLE")

    @app.errorhandler(429)
    def rate_limited(e):
        return _error_response(429, "Too many requests. Please slow down.", "RATE_LIMITED")

    @app.errorhandler(500)
    def internal_error(e):
        logger.error("500 Internal Server Error: %s\n%s", e, traceback.format_exc())
        _log_error_to_db(500, str(e))
        return _error_response(
            500,
            "An internal server error occurred. Please try again later.",
            "INTERNAL_ERROR",
        )

    @app.errorhandler(503)
    def service_unavailable(e):
        return _error_response(
            503,
            "Service temporarily unavailable.",
            "SERVICE_UNAVAILABLE",
        )

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        """Catch-all for any unhandled Python exception."""
        logger.error("Unhandled exception: %s\n%s", e, traceback.format_exc())
        _log_error_to_db(500, repr(e))
        return _error_response(
            500,
            "An unexpected error occurred." if not app.config.get("DEBUG") else str(e),
            "UNEXPECTED_ERROR",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Internal utilities
# ─────────────────────────────────────────────────────────────────────────────

def _get_client_ip() -> str:
    """Return the real client IP, honoring X-Forwarded-For when behind a proxy."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _log_error_to_db(status_code: int, message: str) -> None:
    """Write error details to system_logs without raising secondary exceptions."""
    try:
        from database.database import log_system_event
        log_system_event(
            log_level      = "ERROR",
            source         = "app",
            message        = message[:500],     # cap at 500 chars
            endpoint       = request.path,
            request_method = request.method,
            status_code    = status_code,
            ip_address     = _get_client_ip(),
        )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Root and API index routes (registered directly on the app, not a blueprint)
# ─────────────────────────────────────────────────────────────────────────────

def _register_index_routes(app: Flask) -> None:
    """
    A minimal root route that confirms the API is alive.
    All real endpoints live under /api/* via blueprints.
    """

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "service":     "Mathematical Sequence Prediction System",
            "version":     "1.0.0",
            "status":      "running",
            "docs":        "/api/health/detailed",
            "timestamp":   datetime.now(timezone.utc).isoformat(),
        })

    @app.route("/api", methods=["GET"])
    def api_index():
        return jsonify({
            "success": True,
            "message": "SeqPredict API v1.0 — see /api/health/detailed for system status.",
            "endpoints": {
                "predict":  "POST /api/predict",
                "history":  "GET  /api/history",
                "auth":     "POST /api/auth/login",
                "health":   "GET  /api/health",
            },
        })


# ─────────────────────────────────────────────────────────────────────────────
# Application instance (used by gunicorn and Flask CLI)
# ─────────────────────────────────────────────────────────────────────────────

# Create the app at module level so gunicorn / flask CLI can find it.
# `FLASK_ENV` can be set in the shell or a .env file.
app = create_app()


# ─────────────────────────────────────────────────────────────────────────────
# Development entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Start the Flask development server.

    Environment variables respected:
        FLASK_ENV   — "development" (default) | "production" | "testing"
        FLASK_HOST  — bind address (default: 0.0.0.0)
        FLASK_PORT  — port number  (default: 5000)

    Usage:
        python app.py
        FLASK_PORT=8000 python app.py
    """
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))

    logger.info("Development server starting — http://%s:%d", host, port)

    app.run(
        host    = host,
        port    = port,
        debug   = app.config.get("DEBUG", True),
        use_reloader   = True,
        threaded       = True,    # handle concurrent requests in dev
    )