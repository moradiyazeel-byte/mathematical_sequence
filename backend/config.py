"""
config.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Application Configuration

Three environment classes:
    DevelopmentConfig  — local dev, debug on, verbose logging
    ProductionConfig   — deployment, debug off, strict security
    TestingConfig      — unit/integration tests, in-memory DB

Usage inside app.py:
    from config import config_map, DevelopmentConfig
    app.config.from_object(config_map.get(env, DevelopmentConfig))

Environment variables override any class-level default.
All sensitive values (SECRET_KEY, JWT_SECRET) should be set via env vars
or a .env file — never hard-coded in production.
──────────────────────────────────────────────────────────────────────────────
"""

import os
import secrets
import logging
from datetime import timedelta
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Path anchors
# ─────────────────────────────────────────────────────────────────────────────

# backend/config.py  →  backend/  →  project root
_BACKEND_DIR  = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent


def _load_env_file() -> None:
    """Load key-value pairs from .env into os.environ if not already defined."""
    for env_path in [_PROJECT_ROOT / ".env", _BACKEND_DIR / ".env"]:
        if env_path.exists():
            try:
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v
            except Exception:
                pass


_load_env_file()


# ─────────────────────────────────────────────────────────────────────────────
# Base configuration — all shared defaults
# ─────────────────────────────────────────────────────────────────────────────

class BaseConfig:
    """
    Shared settings inherited by all environment configs.
    Environment variables always take precedence over class attributes.
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    APP_NAME    : str = "Mathematical Sequence Prediction System"
    APP_VERSION : str = "1.0.0"
    API_PREFIX  : str = "/api"

    # ── Security ──────────────────────────────────────────────────────────────
    # IMPORTANT: override SECRET_KEY with a long random value in production.
    # Use: python -c "import secrets; print(secrets.token_hex(48))"
    SECRET_KEY  : str = os.getenv("SECRET_KEY", secrets.token_hex(32))

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY     : str           = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
    JWT_ALGORITHM      : str           = "HS256"
    JWT_ACCESS_EXPIRES : timedelta     = timedelta(hours=24)
    JWT_REFRESH_EXPIRES: timedelta     = timedelta(days=30)

    # ── Database ──────────────────────────────────────────────────────────────
    # Absolute path to the SQLite file in the project-root database/ folder.
    DATABASE_PATH : str = os.getenv(
        "DATABASE_URL",
        os.getenv("DATABASE_PATH", str(_PROJECT_ROOT / "database" / "sequence.db")),
    )
    # Connection pool settings (sqlite3 check_same_thread=False for Flask)
    DATABASE_TIMEOUT  : int  = 30        # seconds before a query times out
    DATABASE_WAL_MODE : bool = True      # Write-Ahead Logging for concurrency

    # ── ML Model ──────────────────────────────────────────────────────────────
    MODEL_PATH : str = os.getenv(
        "MODEL_PATH",
        str(_BACKEND_DIR / "models" / "sequence_model.pkl"),
    )
    MODEL_VERSION_DEFAULT : str = "v1.0.0"

    # ── File uploads ──────────────────────────────────────────────────────────
    UPLOAD_FOLDER      : str   = str(_BACKEND_DIR / "uploads")
    MAX_CONTENT_LENGTH : int   = 5 * 1024 * 1024   # 5 MB hard limit
    ALLOWED_EXTENSIONS : set   = {"csv", "txt"}

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins; "*" in dev only.
    CORS_ORIGINS : str | list = os.getenv("CORS_ORIGINS", "*")

    # ── Prediction limits ─────────────────────────────────────────────────────
    SEQUENCE_MIN_TERMS  : int   = 3
    SEQUENCE_MAX_TERMS  : int   = 50
    SEQUENCE_EPSILON    : float = 0.001    # float comparison tolerance
    CONFIDENCE_THRESHOLD: float = 0.95    # min rule confidence to skip ML

    # ── Pagination ────────────────────────────────────────────────────────────
    HISTORY_PAGE_SIZE   : int = 20
    HISTORY_MAX_LIMIT   : int = 200

    # ── Caching ───────────────────────────────────────────────────────────────
    PREDICTION_CACHE_TTL_HOURS : int = 24   # re-use DB result for identical sequences

    # ── Rate limiting ─────────────────────────────────────────────────────────
    RATELIMIT_DEFAULT        : str = "200 per day;60 per hour;10 per minute"
    RATELIMIT_PREDICT        : str = "100 per hour;5 per minute"
    RATELIMIT_AUTH           : str = "20 per hour;5 per minute"
    RATELIMIT_STORAGE_URL    : str = "memory://"   # swap for redis:// in prod

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL       : str  = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE     : bool = False
    LOG_FILE_PATH   : str  = str(_PROJECT_ROOT / "logs" / "seqpredict.log")
    LOG_MAX_BYTES   : int  = 10 * 1024 * 1024   # 10 MB per log file
    LOG_BACKUP_COUNT: int  = 5

    # ── System ────────────────────────────────────────────────────────────────
    JSON_SORT_KEYS           : bool = False
    PROPAGATE_EXCEPTIONS     : bool = True
    TRAP_HTTP_EXCEPTIONS     : bool = False
    PREFERRED_URL_SCHEME     : str  = "http"
    MAX_DETECTION_TIME_MS    : int  = 200    # warn if prediction exceeds this
    REQUEST_TIMEOUT_SECONDS  : int  = 30

    # ── Password hashing ──────────────────────────────────────────────────────
    BCRYPT_LOG_ROUNDS : int = 12   # work factor; increase for higher security

    # ── Admin ─────────────────────────────────────────────────────────────────
    ADMIN_EMAIL    : str = os.getenv("ADMIN_EMAIL",    "admin@seqpredict.local")
    ADMIN_USERNAME : str = os.getenv("ADMIN_USERNAME", "admin")

    # ── Retraining ────────────────────────────────────────────────────────────
    RETRAIN_FEEDBACK_THRESHOLD : int   = 200    # trigger after this many wrong feedbacks
    RETRAIN_MIN_ACCURACY       : float = 0.88
    RETRAIN_MIN_F1             : float = 0.85

    @classmethod
    def validate(cls) -> None:
        """
        Run sanity checks on critical config values at startup.
        Logs a warning for any value that looks unsafe for production.
        """
        log = logging.getLogger("seqpredict.config")

        if cls.SECRET_KEY and len(cls.SECRET_KEY) < 32:
            log.warning("SECRET_KEY is shorter than 32 characters — use a longer key in production.")

        if cls.JWT_SECRET_KEY and len(cls.JWT_SECRET_KEY) < 32:
            log.warning("JWT_SECRET_KEY is shorter than 32 characters.")

        if cls.DATABASE_PATH.startswith("postgresql://") or cls.DATABASE_PATH.startswith("postgres://"):
            pass
        elif not Path(cls.DATABASE_PATH).parent.exists():
            log.warning("Database directory does not exist: %s", Path(cls.DATABASE_PATH).parent)

        if cls.CORS_ORIGINS == "*":
            log.warning("CORS_ORIGINS is set to '*' — restrict this in production.")

        model = Path(cls.MODEL_PATH)
        if not model.exists():
            log.warning(
                "ML model not found at '%s'. Run training/train_model.py to generate it.",
                cls.MODEL_PATH,
            )

    @classmethod
    def as_dict(cls) -> dict:
        """Return public config values as a dict (excludes secrets and callables)."""
        secrets_keys = {"SECRET_KEY", "JWT_SECRET_KEY", "ADMIN_EMAIL"}
        return {
            k: v
            for k, v in vars(cls).items()
            if not k.startswith("_")
            and not callable(v)
            and k not in secrets_keys
        }


# ─────────────────────────────────────────────────────────────────────────────
# Development configuration
# ─────────────────────────────────────────────────────────────────────────────

class DevelopmentConfig(BaseConfig):
    """
    Settings for local development.
    Debug mode on, verbose logging, permissive CORS.
    """

    DEBUG   : bool = True
    TESTING : bool = False
    ENV     : str  = "development"

    # More readable in dev — stack traces visible in browser
    PROPAGATE_EXCEPTIONS: bool = True

    # Shorter token expiry during dev makes it easier to test auth flows
    JWT_ACCESS_EXPIRES: timedelta = timedelta(hours=48)

    # Lower bcrypt rounds for faster test iterations
    BCRYPT_LOG_ROUNDS: int = 4

    # Verbose logging during development
    LOG_LEVEL: str = "DEBUG"

    # Relax rate limits so manual testing is not interrupted
    RATELIMIT_DEFAULT : str = "10000 per day"
    RATELIMIT_PREDICT : str = "1000 per hour"
    RATELIMIT_AUTH    : str = "200 per hour"

    # Accept all origins in development
    CORS_ORIGINS: str = "*"

    # Shorter cache TTL so re-predictions reflect code changes faster
    PREDICTION_CACHE_TTL_HOURS: int = 1

    # Preferred scheme in dev
    PREFERRED_URL_SCHEME: str = "http"


# ─────────────────────────────────────────────────────────────────────────────
# Production configuration
# ─────────────────────────────────────────────────────────────────────────────

class ProductionConfig(BaseConfig):
    """
    Settings for deployed production environment.
    Debug off, strict security, environment-variable-driven secrets.
    """

    DEBUG   : bool = False
    TESTING : bool = False
    ENV     : str  = "production"

    SECRET_KEY     : str = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    JWT_SECRET_KEY : str = os.getenv("JWT_SECRET_KEY") or secrets.token_hex(32)

    # Restrict CORS to known frontend origin(s) or default to *
    CORS_ORIGINS: str | list = os.getenv("CORS_ORIGINS") or "*"

    # Standard bcrypt work factor for production
    BCRYPT_LOG_ROUNDS: int = 12

    # Shorter JWT token window in production
    JWT_ACCESS_EXPIRES : timedelta = timedelta(hours=12)
    JWT_REFRESH_EXPIRES: timedelta = timedelta(days=14)

    # Write logs to file in production
    LOG_LEVEL   : str  = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE : bool = False

    # Stricter rate limiting in production
    RATELIMIT_DEFAULT : str = "500 per day;100 per hour;15 per minute"
    RATELIMIT_PREDICT : str = "200 per hour;10 per minute"
    RATELIMIT_AUTH    : str = "30 per hour;5 per minute"

    # Longer cache TTL reduces DB load in production
    PREDICTION_CACHE_TTL_HOURS: int = 24

    # HTTPS in production
    PREFERRED_URL_SCHEME: str = "https"

    # Suppress Python exception details from JSON error responses
    PROPAGATE_EXCEPTIONS: bool = False

    @classmethod
    def validate(cls) -> None:
        """Run sanity checks without breaking startup if variables are unset."""
        super().validate()
        log = logging.getLogger("seqpredict.config")

        if not os.getenv("SECRET_KEY"):
            log.warning("SECRET_KEY not set in environment; using auto-generated secret key.")
        if not os.getenv("JWT_SECRET_KEY"):
            log.warning("JWT_SECRET_KEY not set in environment; using auto-generated secret key.")
        if cls.CORS_ORIGINS == "*":
            log.info("CORS_ORIGINS is set to '*' in production.")


# ─────────────────────────────────────────────────────────────────────────────
# Testing configuration
# ─────────────────────────────────────────────────────────────────────────────

class TestingConfig(BaseConfig):
    """
    Settings for automated tests.
    Uses an in-memory SQLite DB so tests are isolated and fast.
    """

    DEBUG   : bool = True
    TESTING : bool = True
    ENV     : str  = "testing"

    # In-memory database — wiped after each test session
    DATABASE_PATH: str = ":memory:"

    # Dummy model path; tests should mock ModelLoader
    MODEL_PATH: str = str(_BACKEND_DIR / "models" / "sequence_model_test.pkl")

    # Instant JWT expiry values for auth tests
    JWT_ACCESS_EXPIRES : timedelta = timedelta(minutes=5)
    JWT_REFRESH_EXPIRES: timedelta = timedelta(minutes=10)

    # Fastest bcrypt for unit tests
    BCRYPT_LOG_ROUNDS: int = 4

    # Disable rate limiting during tests
    RATELIMIT_DEFAULT : str = "99999 per day"
    RATELIMIT_PREDICT : str = "99999 per hour"
    RATELIMIT_AUTH    : str = "99999 per hour"

    # Predictable secret keys for test assertions
    SECRET_KEY     : str = "test-secret-key-not-for-production"
    JWT_SECRET_KEY : str = "test-jwt-secret-key-not-for-production"

    # Accept all CORS origins in tests
    CORS_ORIGINS: str = "*"

    # No caching in tests so every call is evaluated fresh
    PREDICTION_CACHE_TTL_HOURS: int = 0

    # No file logging during tests
    LOG_LEVEL   : str  = "ERROR"
    LOG_TO_FILE : bool = False

    # Lower detection threshold so partially-matching sequences pass
    CONFIDENCE_THRESHOLD: float = 0.60


# ─────────────────────────────────────────────────────────────────────────────
# Config map — resolves environment name → config class
# ─────────────────────────────────────────────────────────────────────────────

config_map: dict[str, type[BaseConfig]] = {
    "development" : DevelopmentConfig,
    "production"  : ProductionConfig,
    "testing"     : TestingConfig,
    # Aliases
    "dev"  : DevelopmentConfig,
    "prod" : ProductionConfig,
    "test" : TestingConfig,
}


# ─────────────────────────────────────────────────────────────────────────────
# Convenience helper — returns the active config class
# ─────────────────────────────────────────────────────────────────────────────

def get_config(env: str | None = None) -> type[BaseConfig]:
    """
    Return the config class for the given environment name.

    Parameters
    ----------
    env : str | None
        Environment name. Falls back to FLASK_ENV env var, then "development".

    Returns
    -------
    type[BaseConfig]
        The matching config class (not an instance).
    """
    resolved = (env or os.getenv("FLASK_ENV", "development")).lower()
    cfg = config_map.get(resolved, DevelopmentConfig)
    cfg.validate()
    return cfg


# ─────────────────────────────────────────────────────────────────────────────
# Quick self-test (python config.py)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    for name, cls in [
        ("development", DevelopmentConfig),
        ("production",  ProductionConfig),
        ("testing",     TestingConfig),
    ]:
        print(f"\n{'─' * 60}")
        print(f"  {name.upper()} CONFIG")
        print(f"{'─' * 60}")
        safe = {
            k: str(v)
            for k, v in cls.as_dict().items()
            if isinstance(v, (str, int, float, bool, timedelta))
        }
        for k, v in sorted(safe.items()):
            print(f"  {k:<36} {v}")

    print("\nconfig.py self-test complete.")