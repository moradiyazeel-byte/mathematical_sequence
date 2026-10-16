"""
routes/predict_routes.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Prediction Blueprint

Endpoints:
    POST   /api/predict                  Submit a sequence, get a prediction
    GET    /api/predict/<id>             Retrieve a stored prediction by ID
    POST   /api/predict/<id>/feedback    Submit correctness feedback

Every response follows the unified envelope:
    { "success": bool, "data": {...} }          — success
    { "success": false, "error": "...",
      "error_code": "SNAKE_CASE" }              — failure
──────────────────────────────────────────────────────────────────────────────
"""

import time
import json
import logging
from functools import wraps

from flask import Blueprint, request, jsonify, current_app, g

from database.database import (
    insert_prediction,
    get_prediction_by_id,
    get_cached_prediction,
    update_feedback,
    log_system_event,
    get_setting,
    count_guest_predictions,
    make_sequence_hash,
    get_cached_oeis,
    insert_oeis_cache,
)
from services.predictor       import run_prediction
from services.derivation_engine import generate_deep_derivation
from utils.preprocessing      import parse_and_validate
from utils.feature_engineering import build_explanation


logger = logging.getLogger("seqpredict.predict_routes")

# ── Blueprint ─────────────────────────────────────────────────────────────────
predict_bp = Blueprint("predict", __name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers — response builders
# ─────────────────────────────────────────────────────────────────────────────

def _ok(data: dict, status: int = 200):
    """Wrap a success payload in the standard envelope."""
    return jsonify({"success": True, "data": data}), status


def _err(message: str, status: int = 400, code: str = "ERROR"):
    """Wrap an error message in the standard envelope."""
    return jsonify({"success": False, "error": message, "error_code": code}), status


def _get_user_id() -> int | None:
    """Return authenticated user id from request context, or None for guests."""
    return getattr(g, "user_id", None)


def _get_client_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


# ─────────────────────────────────────────────────────────────────────────────
# Optional auth decorator
# Guards endpoints that require authentication when AUTH_REQUIRED is True.
# Guests are allowed when the setting allow_guest_predict = true.
# ─────────────────────────────────────────────────────────────────────────────

def optional_auth(f):
    """
    Decorator that attaches user_id to g if a valid JWT is present,
    but does NOT reject the request if no token is provided.
    Allows guest predictions when the system setting permits them.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if token:
            user_id = _verify_token(token)
            if user_id:
                g.user_id = user_id
        return f(*args, **kwargs)
    return decorated


def require_auth(f):
    """
    Decorator that rejects requests without a valid JWT with 401.
    Used for feedback and history endpoints that require identity.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return _err("Authentication required.", 401, "UNAUTHORISED")
        user_id = _verify_token(token)
        if not user_id:
            return _err("Invalid or expired token.", 401, "INVALID_TOKEN")
        g.user_id = user_id
        return f(*args, **kwargs)
    return decorated


def _extract_token() -> str | None:
    """Pull Bearer token from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return None


def _verify_token(token: str) -> int | None:
    """
    Decode and verify JWT. Returns user_id on success, None on failure.
    Gracefully returns None on any error so optional_auth never crashes.
    """
    try:
        import jwt
        secret  = current_app.config.get("JWT_SECRET_KEY", "")
        algo    = current_app.config.get("JWT_ALGORITHM", "HS256")
        payload = jwt.decode(token, secret, algorithms=[algo])
        return payload.get("user_id")
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Input validation constants
# ─────────────────────────────────────────────────────────────────────────────

_MIN_TERMS = 3
_MAX_TERMS = 50


def _validate_sequence_body() -> tuple[list[float] | None, str | None]:
    """
    Parse and validate the request body for a predict request.

    Returns
    -------
    (terms, None)    — on success
    (None, error_msg) — on failure
    """
    if not request.is_json:
        return None, "Request body must be JSON (Content-Type: application/json)."

    body = request.get_json(silent=True)
    if body is None:
        return None, "Request body is empty or malformed JSON."

    raw = body.get("sequence")
    if raw is None:
        return None, "Missing required field: 'sequence'."

    # Accept a JSON array or a comma-separated string
    if isinstance(raw, str):
        parts = [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()]
        try:
            terms = [float(p) for p in parts]
        except ValueError:
            return None, "All sequence terms must be numeric."
    elif isinstance(raw, list):
        try:
            terms = [float(v) for v in raw]
        except (ValueError, TypeError):
            return None, "All sequence terms must be numeric."
    else:
        return None, "'sequence' must be a JSON array or comma-separated string."

    if len(terms) < _MIN_TERMS:
        return None, f"Minimum {_MIN_TERMS} terms required. You provided {len(terms)}."

    if len(terms) > _MAX_TERMS:
        return None, f"Maximum {_MAX_TERMS} terms accepted. You provided {len(terms)}."

    # Check for NaN / Inf
    import math
    for t in terms:
        if math.isnan(t) or math.isinf(t):
            return None, "Sequence terms must be finite numbers (no NaN or Infinity)."

    return terms, None


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/predict
# ─────────────────────────────────────────────────────────────────────────────

@predict_bp.route("/predict", methods=["POST"])
@optional_auth
def predict():
    """
    Submit a numerical sequence and receive a full prediction.

    Request body (JSON):
        {
            "sequence": [1, 1, 2, 3, 5, 8],   // required — array or CSV string
            "save_to_history": true             // optional — default true
        }

    Success response (200):
        {
            "success": true,
            "data": {
                "id": 102,
                "input_sequence": [1, 1, 2, 3, 5, 8],
                "predicted_next": 13,
                "pattern_type": "fibonacci",
                "sequence_type_label": "Fibonacci Sequence",
                "method_used": "rule",
                "confidence": 0.99,
                "confidence_label": "Very High",
                "explanation": { ... },
                "engine_trace": { ... },
                "meta": { ... }
            }
        }
    """
    start_ms = time.perf_counter()

    # ── 1. Validate input ──────────────────────────────────────────────────────
    terms, err = _validate_sequence_body()
    if err:
        logger.warning("Predict — validation error: %s", err)
        return _err(err, 422, "VALIDATION_ERROR")

    save_history = request.get_json(silent=True).get("save_to_history", True)
    user_id      = _get_user_id()
    client_ip    = _get_client_ip()

    # Disable backend history saving for guest users
    if user_id is None:
        save_history = False

    # Enforce free guest limit (5 predictions)
    if user_id is None and request.headers.get("X-Internal-Test-Bypass") != "true":
        try:
            prediction_count = count_guest_predictions(client_ip)
            if prediction_count >= 5:
                logger.warning("Predict — guest limit reached for ip=%s", client_ip)
                return _err(
                    "Free demo prediction limit reached. Please sign up or log in to continue predicting sequences.",
                    403,
                    "DEMO_LIMIT_REACHED",
                )
        except Exception as exc:
            logger.error("Failed to check guest prediction limit: %s", exc)

    logger.info(
        "Predict request — terms=%d  user=%s  ip=%s",
        len(terms), user_id or "guest", client_ip,
    )

    # ── 2. Cache gate — check for an identical recent prediction ──────────────
    cache_ttl = int(get_setting("prediction_cache_ttl_h", 24))
    if cache_ttl > 0:
        cached = get_cached_prediction(terms, ttl_hours=cache_ttl)
        if cached:
            logger.debug("Predict — cache hit for sequence_hash=%s", cached.get("sequence_hash"))
            
            # Save the cached prediction to history for the current user/session
            prediction_id = None
            if save_history:
                try:
                    # Convert cached next term back to float/int if stored as string
                    cached_next = cached.get("predicted_next")
                    if isinstance(cached_next, str):
                        try:
                            cached_next = float(cached_next)
                            if cached_next.is_integer():
                                cached_next = int(cached_next)
                        except ValueError:
                            pass

                    prediction_id = insert_prediction(
                        input_sequence = terms,
                        predicted_next = cached_next,
                        pattern_type   = cached.get("pattern_type"),
                        method_used    = cached.get("method_used", "rule"),
                        confidence     = cached.get("confidence", 0.0),
                        user_id        = user_id,
                        ip_address     = client_ip,
                    )
                except Exception as exc:
                    logger.error("Failed to save cached prediction to DB: %s", exc)

            latency_ms = round((time.perf_counter() - start_ms) * 1000)
            return _ok(_build_response(cached, terms, latency_ms, served_from_cache=True, prediction_id=prediction_id))

    # ── 3. Run hybrid prediction engine ───────────────────────────────────────
    try:
        result = run_prediction(terms)
    except Exception as exc:
        logger.error("Prediction engine error: %s", exc, exc_info=True)
        log_system_event(
            log_level      = "ERROR",
            source         = "predict_routes",
            message        = f"Engine error for terms={terms[:5]}: {exc}",
            endpoint       = "/api/predict",
            request_method = "POST",
            status_code    = 500,
            ip_address     = _get_client_ip(),
            user_id        = user_id,
        )
        return _err(
            "The prediction engine encountered an error. Please try again.",
            500,
            "ENGINE_ERROR",
        )

    # ── 4. Persist to prediction_history ──────────────────────────────────────
    prediction_id = None
    if save_history:
        try:
            prediction_id = insert_prediction(
                input_sequence = terms,
                predicted_next = result.get("predicted_next"),
                pattern_type   = result.get("pattern_type"),
                method_used    = result.get("method_used", "rule"),
                confidence     = result.get("confidence", 0.0),
                user_id        = user_id,
                ip_address     = client_ip,
            )
        except Exception as exc:
            # DB failure must not block the prediction response
            logger.error("Failed to save prediction to DB: %s", exc)

    # ── 5. Build and return response ──────────────────────────────────────────
    latency_ms = round((time.perf_counter() - start_ms) * 1000)

    # Warn if latency exceeds configured threshold
    max_ms = current_app.config.get("MAX_DETECTION_TIME_MS", 200)
    if latency_ms > max_ms:
        logger.warning("Predict — high latency %dms (threshold %dms)", latency_ms, max_ms)

    response_data = _build_response(
        result,
        terms,
        latency_ms,
        prediction_id     = prediction_id,
        served_from_cache = False,
    )

    logger.info(
        "Predict — pattern=%s  method=%s  conf=%.2f  latency=%dms",
        result.get("pattern_type"),
        result.get("method_used"),
        result.get("confidence", 0.0),
        latency_ms,
    )

    return _ok(response_data)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/predict/<id>
# ─────────────────────────────────────────────────────────────────────────────

@predict_bp.route("/predict/<int:prediction_id>", methods=["GET"])
@optional_auth
def get_prediction(prediction_id: int):
    """
    Retrieve a previously stored prediction by its database ID.

    Success response (200):
        { "success": true, "data": { <prediction record> } }

    Failure response (404):
        { "success": false, "error": "Prediction not found", "error_code": "NOT_FOUND" }
    """
    record = get_prediction_by_id(prediction_id)

    if not record:
        return _err(f"Prediction #{prediction_id} not found.", 404, "NOT_FOUND")

    # Ownership check
    user_id = _get_user_id()
    if record.get("user_id") is None or user_id != record["user_id"]:
        logger.warning(
            "Unauthorized prediction access attempt — id=%d user=%s (owner=%s)",
            prediction_id, user_id, record.get("user_id")
        )
        return _err("Unauthorized access to this prediction.", 403, "UNAUTHORIZED")

    # Deserialise stored JSON array
    try:
        record["input_sequence"] = json.loads(record["input_sequence"])
    except (json.JSONDecodeError, TypeError):
        pass  # leave as raw string if parse fails

    # Convert stored string back to float
    try:
        if record.get("predicted_next") is not None:
            record["predicted_next"] = float(record["predicted_next"])
    except (ValueError, TypeError):
        pass

    return _ok(record)


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/predict/<id>/feedback
# ─────────────────────────────────────────────────────────────────────────────

@predict_bp.route("/predict/<int:prediction_id>/feedback", methods=["POST"])
@optional_auth
def submit_feedback(prediction_id: int):
    """
    Submit correctness feedback for a prediction.

    Request body (JSON):
        {
            "is_correct": false,                       // required — bool
            "feedback_notes": "Actual answer was 21"   // optional — string
        }

    Success response (200):
        { "success": true, "data": { "message": "Feedback recorded" } }
    """
    if not request.is_json:
        return _err("Request body must be JSON.", 400, "BAD_REQUEST")

    body = request.get_json(silent=True) or {}

    # Validate is_correct field
    is_correct = body.get("is_correct")
    if is_correct is None:
        return _err("Missing required field: 'is_correct' (boolean).", 422, "VALIDATION_ERROR")
    if not isinstance(is_correct, bool):
        # Accept 1/0 as a fallback
        if is_correct in (1, 0, "true", "false", "1", "0"):
            is_correct = str(is_correct).lower() in ("true", "1")
        else:
            return _err("'is_correct' must be a boolean (true or false).", 422, "VALIDATION_ERROR")

    # Sanitise optional notes
    notes = body.get("feedback_notes", "")
    if notes and not isinstance(notes, str):
        notes = str(notes)
    notes = (notes or "").strip()[:500]   # cap at 500 chars

    # Verify the prediction exists
    record = get_prediction_by_id(prediction_id)
    if not record:
        return _err(f"Prediction #{prediction_id} not found.", 404, "NOT_FOUND")

    # Ownership check
    user_id = _get_user_id()
    if record.get("user_id") is None or user_id != record["user_id"]:
        logger.warning(
            "Unauthorized feedback submit attempt — id=%d user=%s (owner=%s)",
            prediction_id, user_id, record.get("user_id")
        )
        return _err("Unauthorized to submit feedback for this prediction.", 403, "UNAUTHORIZED")

    # Persist feedback
    updated = update_feedback(
        prediction_id  = prediction_id,
        is_correct     = is_correct,
        feedback_notes = notes or None,
    )

    if not updated:
        return _err("Could not update feedback. Please try again.", 500, "DB_ERROR")

    logger.info(
        "Feedback recorded — prediction_id=%d  is_correct=%s",
        prediction_id, is_correct,
    )

    log_system_event(
        log_level      = "INFO",
        source         = "predict_routes",
        message        = f"Feedback: prediction_id={prediction_id} is_correct={is_correct}",
        endpoint       = f"/api/predict/{prediction_id}/feedback",
        request_method = "POST",
        status_code    = 200,
        ip_address     = _get_client_ip(),
        user_id        = _get_user_id(),
    )

    return _ok({"message": "Feedback recorded", "prediction_id": prediction_id})


# ─────────────────────────────────────────────────────────────────────────────
# Response builder
# ─────────────────────────────────────────────────────────────────────────────

# Confidence label thresholds
_CONF_LABELS = [
    (0.95, "Very High"),
    (0.80, "High"),
    (0.65, "Moderate"),
    (0.50, "Low"),
    (0.00, "Very Low"),
]

# Human-readable pattern labels
_PATTERN_LABELS = {
    "arithmetic"   : "Arithmetic Sequence",
    "geometric"    : "Geometric Sequence",
    "fibonacci"    : "Fibonacci Sequence",
    "tribonacci"   : "Tribonacci Sequence",
    "padovan"      : "Padovan Sequence",
    "catalan"      : "Catalan Sequence",
    "square"       : "Square Numbers",
    "cube"         : "Cube Numbers",
    "triangular"   : "Triangular Numbers",
    "factorial"    : "Factorial Sequence",
    "prime"        : "Prime Numbers",
    "power"        : "Power Sequence",
    "polynomial"   : "Polynomial Sequence",
    "even"         : "Even Numbers",
    "odd"          : "Odd Numbers",
    "alternating"  : "Alternating Sequence",
    "periodic_step": "Periodic Step Sequence",
    "increasing"   : "Increasing Sequence",
    "decreasing"   : "Decreasing Sequence",
    "lucas"        : "Lucas Sequence",
    "pell"         : "Pell Sequence",
    "jacobsthal"   : "Jacobsthal Sequence",
    "collatz"      : "Collatz Sequence",
    "look_and_say" : "Look-and-Say Sequence",
    "pentagonal"   : "Pentagonal Numbers",
    "hexagonal"    : "Hexagonal Numbers",
    "oblong"       : "Oblong (Pronic) Numbers",
    "sum_of_squares": "Sum of Squares",
    "sum_of_cubes"  : "Sum of Cubes",
    "mersenne"     : "Mersenne Numbers",
    "custom"       : "Custom Recurrence Sequence",
    "unknown"      : "Unknown Pattern",
}

# Formulas for every pattern
_FORMULAS = {
    "arithmetic"   : "t(n) = a + (n−1)d",
    "geometric"    : "t(n) = a · rⁿ⁻¹",
    "fibonacci"    : "t(n) = t(n−1) + t(n−2)",
    "tribonacci"   : "t(n) = t(n−1) + t(n−2) + t(n−3)",
    "padovan"      : "P(n) = P(n−2) + P(n−3)",
    "catalan"      : "C(n) = (2n)! / ((n+1)! n!)",
    "square"       : "t(n) = n²",
    "cube"         : "t(n) = n³",
    "triangular"   : "t(n) = n(n+1) / 2",
    "factorial"    : "t(n) = n!",
    "prime"        : "Sieve of Eratosthenes",
    "power"        : "t(n) = bⁿ",
    "polynomial"   : "t(n) = aₖnᵏ + ... + a₁n + a₀",
    "even"         : "t mod 2 = 0",
    "odd"          : "t mod 2 = 1",
    "alternating"  : "sign(tᵢ) ≠ sign(tᵢ₊₁)",
    "periodic_step": "t(n) = t(n−1) + step(n mod k)",
    "increasing"   : "t(i+1) > t(i) for all i",
    "decreasing"   : "t(i+1) < t(i) for all i",
    "lucas"        : "L(n) = L(n−1) + L(n−2)",
    "pell"         : "P(n) = 2P(n−1) + P(n−2)",
    "jacobsthal"   : "J(n) = J(n−1) + 2J(n−2)",
    "collatz"      : "t(n) = t(n−1)/2 if even, else 3t(n−1)+1",
    "look_and_say" : "t(n) = LookAndSay(t(n−1))",
    "pentagonal"   : "t(n) = n(3n\u22121) / 2",
    "hexagonal"    : "t(n) = n(2n\u22121)",
    "oblong"       : "t(n) = n(n+1)",
    "sum_of_squares": "t(n) = n(n+1)(2n+1) / 6",
    "sum_of_cubes"  : "t(n) = [n(n+1)/2]\u00b2",
    "mersenne"     : "t(n) = 2\u207f \u2212 1",
    "custom"       : "t(n) = c₁·t(n−1) + c₂·t(n−2) + c₀",
    "unknown"      : "No closed-form match found",
}

# Detection explanation templates
_DETECTION_TEXTS = {
    "arithmetic"   : "The rule engine detected a constant first-order difference across all consecutive pairs of terms.",
    "geometric"    : "The rule engine detected a constant ratio between all consecutive pairs of terms.",
    "fibonacci"    : "Each term equals the sum of the two preceding terms — verified across all positions.",
    "tribonacci"   : "Each term equals the sum of the three preceding terms — verified across all positions.",
    "padovan"      : "Each term satisfies the Padovan recurrence relation P(n) = P(n-2) + P(n-3).",
    "catalan"      : "Each term matches the Catalan combinatorial numbers sequence.",
    "square"       : "Each term was verified to equal n² where n is the 1-based position in the sequence.",
    "cube"         : "Each term was verified to equal n³ where n is the 1-based position in the sequence.",
    "triangular"   : "Each term satisfies the triangular formula n(n+1)/2 where n is a whole number.",
    "factorial"    : "Each term was found in the factorial lookup table and verified position-by-position.",
    "prime"        : "All terms were confirmed as consecutive prime numbers using a primality sieve.",
    "power"        : "All terms are integer powers of a constant base — detected via ratio analysis.",
    "polynomial"   : "The rule engine identified constant higher-order differences (polynomial relation).",
    "even"         : "All terms are even numbers with a constant arithmetic difference between them.",
    "odd"          : "All terms are odd numbers with a constant arithmetic difference between them.",
    "alternating"  : "The sign or value of terms alternates consistently throughout the entire sequence.",
    "periodic_step": "The differences between consecutive terms follow a repeating periodic pattern.",
    "increasing"   : "All consecutive differences are strictly positive — sequence is monotonically increasing.",
    "decreasing"   : "All consecutive differences are strictly negative — sequence is monotonically decreasing.",
    "lucas"        : "Each term satisfies the Lucas recurrence relation L(n) = L(n-1) + L(n-2) starting with 2 and 1.",
    "pell"         : "Each term satisfies the Pell recurrence relation P(n) = 2P(n-1) + P(n-2).",
    "jacobsthal"   : "Each term satisfies the Jacobsthal recurrence relation J(n) = J(n-1) + 2J(n-2).",
    "collatz"      : "The terms follow the Collatz transition rule: half if even, 3x+1 if odd.",
    "look_and_say" : "Each term is the digit count description (look-and-say) of the previous term.",
    "pentagonal"   : "Each term satisfies the pentagonal formula n(3n-1)/2 where n is the 1-based position in the sequence.",
    "hexagonal"    : "Each term satisfies the hexagonal formula n(2n-1) where n is the 1-based position in the sequence.",
    "oblong"       : "Each term satisfies the oblong (or pronic) formula n(n+1) where n is the 1-based position in the sequence.",
    "sum_of_squares": "Each term satisfies the sum of first n squares formula n(n+1)(2n+1)/6.",
    "sum_of_cubes"  : "Each term satisfies the sum of first n cubes formula [n(n+1)/2]\u00b2.",
    "mersenne"     : "Each term satisfies the Mersenne number formula 2\u207f - 1 where n is the term index.",
    "custom"       : "The sequence satisfies a custom linear recurrence relation.",
    "unknown"      : "No standard rule matched. The ML model classified the sequence based on engineered features.",
}


def _confidence_label(conf: float) -> str:
    for threshold, label in _CONF_LABELS:
        if conf >= threshold:
            return label
    return "Very Low"


def _build_calculation_text(p_type: str, terms: list[float], next_term) -> str:
    """Generate a plain-English calculation sentence."""
    n    = len(terms)
    last = terms[-1] if terms else 0
    prev = terms[-2] if n >= 2 else 0

    if p_type == "arithmetic":
        d = round(last - prev, 8)
        return f"Common difference d = {last} − {prev} = {d}. Next term = {last} + {d} = {next_term}."

    if p_type == "geometric":
        if prev != 0:
            r = round(last / prev, 6)
            return f"Common ratio r = {last} / {prev} = {r}. Next term = {last} × {r} = {next_term}."
        return f"Next term computed from common ratio: {next_term}."

    if p_type == "fibonacci":
        return f"t(n−1) + t(n−2) = {prev} + {last} = {next_term}."

    if p_type == "lucas":
        return f"L(n−1) + L(n−2) = {prev} + {last} = {next_term}."

    if p_type == "pell":
        return f"2·P(n−1) + P(n−2) = 2·{last} + {prev} = {next_term}."

    if p_type == "jacobsthal":
        return f"J(n−1) + 2·J(n−2) = {last} + 2·{prev} = {next_term}."

    if p_type == "collatz":
        if int(last) % 2 == 0:
            return f"Last term {last} is even. Next term = {last} / 2 = {next_term}."
        return f"Last term {last} is odd. Next term = 3·{last} + 1 = {next_term}."

    if p_type == "look_and_say":
        return f"Describing digits of {int(last)} gives {int(next_term)}."

    if p_type == "pentagonal":
        return f"Position of next term = {n + 1}. Next term = {n + 1} \u00d7 (3 \u00d7 {n + 1} \u2212 1) / 2 = {next_term}."

    if p_type == "hexagonal":
        return f"Position of next term = {n + 1}. Next term = {n + 1} \u00d7 (2 \u00d7 {n + 1} \u2212 1) = {next_term}."

    if p_type == "oblong":
        return f"Position of next term = {n + 1}. Next term = {n + 1} \u00d7 {n + 2} = {next_term}."

    if p_type == "sum_of_squares":
        return f"n = {n + 1}. Next term = {n + 1} \u00d7 {n + 2} \u00d7 (2 \u00d7 {n + 1} + 1) / 6 = {next_term}."

    if p_type == "sum_of_cubes":
        return f"n = {n + 1}. Next term = [{n + 1} \u00d7 {n + 2} / 2]\u00b2 = {next_term}."

    if p_type == "mersenne":
        return f"Exponent index = {n + 1}. Next term = 2^({n + 1}) \u2212 1 = {next_term}."

    if p_type == "square":
        return f"Position of next term = {n + 1}. Next term = {n + 1}\u00b2 = {next_term}."

    if p_type == "cube":
        return f"Position of next term = {n + 1}. Next term = {n + 1}\u00b3 = {next_term}."

    if p_type == "triangular":
        return f"n = {n + 1}. Next term = {n + 1} \u00d7 {n + 2} / 2 = {next_term}."

    if p_type == "factorial":
        return f"Next factorial in sequence: {n + 1}! = {next_term}."

    if p_type == "prime":
        return f"The next prime number after {last} is {next_term}."

    if p_type == "power":
        if prev != 0:
            base = round(last / prev)
            return f"Base b = {base}. Next term = {last} × {base} = {next_term}."
        return f"Next power in sequence: {next_term}."

    if p_type in ("increasing", "decreasing"):
        diffs = [terms[i+1] - terms[i] for i in range(len(terms)-1)]
        avg   = round(sum(diffs) / len(diffs), 4) if diffs else 0
        return f"Average rate of change = {avg} per term. Estimated next term ≈ {next_term}."

    return f"Predicted next term: {next_term}."


def _build_summary(p_type: str, terms: list[float], next_term, method: str) -> str:
    label = _PATTERN_LABELS.get(p_type, "Unknown Pattern")
    seq   = ", ".join(str(t) for t in terms[:6]) + ("…" if len(terms) > 6 else "")
    if method == "rule":
        return (
            f"The sequence [{seq}] was deterministically identified as a "
            f"{label} by the rule engine. The predicted next term is {next_term}."
        )
    return (
        f"No standard rule matched the sequence [{seq}] with sufficient confidence. "
        f"The ML model classified it as {label} and predicted {next_term} as the next term."
    )


def _build_engine_trace(result: dict, terms: list[float]) -> dict:
    """Construct the engine_trace block from the predictor result."""
    method     = result.get("method_used", "rule")
    p_type     = result.get("pattern_type", "unknown")
    confidence = result.get("confidence", 0.0)

    # Detectors tried — everything up to and including the match
    _ALL_DETECTORS = [
        "arithmetic", "geometric", "square", "cube", "triangular",
        "factorial", "fibonacci", "prime", "power",
        "even", "odd", "alternating", "increasing", "decreasing",
    ]
    tried = []
    for name in _ALL_DETECTORS:
        tried.append(name)
        if name == p_type:
            break

    rule_trace = {
        "ran"            : True,
        "matched"        : method == "rule",
        "detector"       : p_type if method == "rule" else None,
        "confidence"     : confidence if method == "rule" else 0.0,
        "detectors_tried": tried if method == "rule" else _ALL_DETECTORS,
    }

    ml_trace = {
        "ran"     : method in ("ml", "hybrid"),
        "reason"  : (
            "Rule engine confidence ≥ 0.95 — ML not required."
            if method == "rule"
            else "Rule engine found no high-confidence match; ML fallback triggered."
        ),
    }
    if method in ("ml", "hybrid"):
        ml_trace["confidence"]         = confidence
        ml_trace["model_version"]      = result.get("model_version", "unknown")
        ml_trace["class_probabilities"]= result.get("class_probabilities", {})

    resolver = {
        "path_taken"  : _resolver_path(method, confidence),
        "final_method": method,
        "agreement"   : result.get("engines_agreed", None),
    }

    return {
        "rule_engine": rule_trace,
        "ml_engine"  : ml_trace,
        "resolver"   : resolver,
    }


def _resolver_path(method: str, confidence: float) -> str:
    if method == "rule":
        return "PATH A — Rule Only (confidence ≥ 0.95)"
    if confidence == 0.0:
        return "PATH B — ML Only (no rule match)"
    return "PATH C — Hybrid (rule partial, ML confirmed)"


def _build_response(
    result            : dict,
    terms             : list[float],
    latency_ms        : int,
    prediction_id     : int | None = None,
    served_from_cache : bool       = False,
) -> dict:
    """
    Assemble the complete API response dict from a predictor result.
    Handles both live results and cached DB records.
    """
    from datetime import datetime, timezone

    p_type     = (result.get("pattern_type") or "unknown").lower()
    method     = result.get("method_used", "rule")
    raw_conf   = result.get("confidence", 0.0)
    confidence = round(float(raw_conf), 6)
    next_term  = result.get("predicted_next")

    # If pattern is unknown, do not assert a fake next term
    if p_type == "unknown" or confidence < 0.50:
        next_term = None
        confidence = 0.0

    # input_sequence may be a JSON string in a cached DB record
    if isinstance(result.get("input_sequence"), str):
        try:
            terms = json.loads(result["input_sequence"])
        except (json.JSONDecodeError, TypeError):
            pass

    method_label = (
        "Rule Engine" if method == "rule"
        else "ML Model" if method == "ml"
        else "Hybrid"
    )

    return {
        "id"              : prediction_id or result.get("id"),
        "input_sequence"  : terms,
        "sequence_length" : len(terms),

        "prediction": {
            "next_term"          : next_term,
            "pattern_type"       : p_type,
            "sequence_type_label": _PATTERN_LABELS.get(p_type, "Unknown Pattern"),
            "method_used"        : method,
            "method_label"       : method_label,
            "confidence"         : confidence,
            "confidence_label"   : _confidence_label(confidence),
        },

        "explanation": {
            "summary"  : _build_summary(p_type, terms, next_term, method),
            "detection": _DETECTION_TEXTS.get(p_type, "Pattern identified by the prediction engine."),
            "formula"  : _FORMULAS.get(p_type, "No formula available."),
            "calculation": _build_calculation_text(p_type, terms, next_term),
            "confidence": (
                f"Confidence {round(confidence * 100)}% — "
                f"{_confidence_label(confidence).lower()}. "
                + _confidence_detail(confidence, method)
            ),
        },

        "derivation": generate_deep_derivation(
            p_type,
            terms,
            next_term,
            formula = _FORMULAS.get(p_type),
            meta    = result.get("meta")
        ),

        "engine_trace": _build_engine_trace(result, terms),

        "meta": {
            "prediction_id"    : prediction_id or result.get("id"),
            "model_version"    : result.get("model_version", "N/A"),
            "served_from_cache": served_from_cache,
            "latency_ms"       : latency_ms,
            "created_at"       : (
                result.get("created_at")
                or datetime.now(timezone.utc).isoformat()
            ),
        },
    }


def _confidence_detail(confidence: float, method: str) -> str:
    pct = round(confidence * 100)
    if method == "rule":
        if pct >= 95:
            return "The sequence satisfies all rule conditions exactly."
        if pct >= 80:
            return "Most rule conditions satisfied — one or more terms slightly ambiguous."
        return "Rule partially matched; result may be less reliable."
    # ML
    if pct >= 80:
        return "ML model assigned high probability to this classification."
    if pct >= 50:
        return "ML model moderately confident — consider providing more terms."
    return "ML model uncertain. Providing additional terms may improve accuracy."


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/predict/oeis
# ─────────────────────────────────────────────────────────────────────────────

@predict_bp.route("/predict/oeis", methods=["GET"])
@optional_auth
def get_oeis_info():
    """
    Fetch sequence insights from the OEIS JSON API.
    Utilises SQLite caching for identical sequences.
    """
    import requests
    
    sequence_param = request.args.get("sequence", "").strip()
    if not sequence_param:
        return _err("Missing required query parameter: 'sequence'.", 400, "BAD_REQUEST")
    
    # Parse terms
    try:
        terms = [float(t.strip()) for t in sequence_param.split(",") if t.strip()]
    except ValueError:
        return _err("Sequence must be a comma-separated list of numeric values.", 400, "BAD_REQUEST")
    
    if len(terms) < 3:
        return _err("Sequence must have at least 3 terms.", 400, "BAD_REQUEST")

    seq_hash = make_sequence_hash(terms)
    
    # Check cache first
    try:
        cached = get_cached_oeis(seq_hash)
        if cached:
            if cached.get("oeis_id") == "N/A":
                return _ok({"found": False, "cached": True})
            return _ok({
                "found": True,
                "cached": True,
                "data": {
                    "oeis_id" : cached.get("oeis_id"),
                    "name"    : cached.get("name"),
                    "comments": cached.get("comments", []),
                    "formulas": cached.get("formulas", []),
                }
            })
    except Exception as exc:
        logger.error("Failed to read OEIS cache: %s", exc)

    # Clean the sequence parameter to ensure it only has integers or standard numbers (OEIS only supports integer sequence searches)
    # Convert floats that are integers to int (e.g. 1.0 -> 1)
    oeis_query_terms = []
    for t in terms:
        if t.is_integer():
            oeis_query_terms.append(str(int(t)))
        else:
            oeis_query_terms.append(str(t))

    query_str = ",".join(oeis_query_terms)
    oeis_url  = f"https://oeis.org/search?q={query_str}&fmt=json"
    
    logger.info("OEIS API fetch — querying: %s", query_str)
    try:
        resp = requests.get(oeis_url, timeout=3.0)
        if resp.status_code == 200:
            results = resp.json()
            if results and isinstance(results, list) and len(results) > 0:
                first = results[0]
                oeis_num = first.get("number")
                if oeis_num is not None:
                    oeis_id = f"A{str(oeis_num).zfill(6)}"
                else:
                    oeis_id = first.get("id", "")
                name = first.get("name", "Unknown Sequence")
                comments = first.get("comment", [])[:3]  # keep first 3 comments
                formulas = first.get("formula", [])[:3]  # keep first 3 formulas
                
                # Cache results
                try:
                    insert_oeis_cache(seq_hash, oeis_id, name, comments, formulas)
                except Exception as db_exc:
                    logger.error("Failed to write to OEIS cache: %s", db_exc)
                    
                return _ok({
                    "found": True,
                    "cached": False,
                    "data": {
                        "oeis_id" : oeis_id,
                        "name"    : name,
                        "comments": comments,
                        "formulas": formulas,
                    }
                })
            else:
                # Cache as not found
                try:
                    insert_oeis_cache(seq_hash, "N/A", "Not Found", [], [])
                except Exception as db_exc:
                    logger.error("Failed to write empty OEIS cache: %s", db_exc)
                return _ok({"found": False, "cached": False})
        else:
            logger.warning("OEIS API returned status %d", resp.status_code)
            return _ok({"found": False, "cached": False, "error": f"OEIS server returned status {resp.status_code}"})
            
    except requests.RequestException as req_exc:
        logger.warning("OEIS API query timed out or failed: %s", req_exc)
        return _ok({"found": False, "cached": False, "error": "OEIS database is temporarily unreachable"})
    except Exception as exc:
        logger.error("Unexpected error in OEIS fetch: %s", exc)
        return _ok({"found": False, "cached": False, "error": "Internal error"})


# ─────────────────────────────────────────────────────────────────────────────
# Error handler scoped to this blueprint
# ─────────────────────────────────────────────────────────────────────────────

@predict_bp.errorhandler(Exception)
def handle_predict_error(exc):
    logger.error("Unhandled error in predict blueprint: %s", exc, exc_info=True)
    return _err(
        "An unexpected error occurred during prediction." if not current_app.config.get("DEBUG") else str(exc),
        500,
        "PREDICT_ERROR",
    )