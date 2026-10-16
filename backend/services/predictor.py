"""
services/predictor.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Hybrid Prediction Orchestrator

This module is the single entry point for all prediction requests.
It implements the three-layer hybrid architecture:

    Layer 1 — Rule Engine   (sequence_detector.py)
    Layer 2 — ML Engine     (model_loader.py)
    Layer 3 — Hybrid Resolver (this file)

Public API:
    run_prediction(terms: list[float]) -> dict

The returned dict is consumed by predict_routes.py to build the JSON
response sent to the frontend.

Decision matrix (Hybrid Resolver):
    Rule conf ≥ 0.95            → PATH A: rule result returned directly
    Rule conf == 0.00           → PATH B: ML result only
    0.60 ≤ rule conf < 0.95     → PATH C: compare rule vs ML, pick higher
    Both engines agree          → PATH D: agreement bonus (+0.05 conf, capped at 1.0)
    Engines disagree            → PATH E: higher confidence wins, small penalty applied
──────────────────────────────────────────────────────────────────────────────
"""

import logging
import traceback
from datetime import datetime, timezone
from typing   import Any

from flask import current_app


logger = logging.getLogger("seqpredict.predictor")


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

# Minimum rule confidence to skip ML entirely (Path A)
_RULE_ACCEPT_THRESHOLD   : float = 0.95

# Minimum rule confidence to still try ML as a cross-check (Path C)
_RULE_PARTIAL_THRESHOLD  : float = 0.60

# ML must beat rule by this margin to override it (Path C)
_ML_OVERRIDE_MARGIN      : float = 0.10

# Agreement bonus applied when both engines return the same pattern
_AGREEMENT_BONUS         : float = 0.05

# Disagreement penalty applied to the winning engine's confidence
_DISAGREEMENT_PENALTY    : float = 0.05

# Fallback next-term confidence when ML cannot compute a numeric prediction
_ML_FALLBACK_CONFIDENCE  : float = 0.40


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def run_prediction(terms: list[float]) -> dict:
    """
    Run the full hybrid prediction pipeline for a given sequence.

    Parameters
    ----------
    terms : list[float]
        Validated, normalised sequence terms (min 3, max 50).

    Returns
    -------
    dict with keys:
        pattern_type        str   — detected family name (e.g. "fibonacci")
        predicted_next      float — next term value
        method_used         str   — "rule" | "ml" | "hybrid"
        confidence          float — 0.0–1.0
        model_version       str   — active model version or "N/A"
        engines_agreed      bool  — True when both engines returned same pattern
        class_probabilities dict  — ML class probabilities (empty for rule-only)
        resolver_path       str   — which decision path was taken
        rule_result         dict  — raw rule engine output (for tracing)
        ml_result           dict  — raw ML engine output  (for tracing; None if not run)
    """

    logger.debug("run_prediction — terms=%s", terms[:8])

    # ── Layer 1: Rule Engine ──────────────────────────────────────────────────
    rule_result = _run_rule_engine(terms)
    rule_conf   = rule_result.get("confidence", 0.0)

    logger.debug(
        "Rule engine → pattern=%s  conf=%.3f",
        rule_result.get("pattern_type"), rule_conf,
    )

    # ── Path A: Strong rule match — skip ML entirely ──────────────────────────
    if rule_conf >= _RULE_ACCEPT_THRESHOLD:
        logger.debug("PATH A — rule accepted (conf=%.3f ≥ %.2f)", rule_conf, _RULE_ACCEPT_THRESHOLD)
        return _build_final(
            winner          = rule_result,
            method          = "rule",
            ml_result       = None,
            engines_agreed  = None,
            resolver_path   = "PATH A — Rule Only",
            terms           = terms,
        )

    # ── Layer 2: ML Engine ────────────────────────────────────────────────────
    ml_result = _run_ml_engine(terms, rule_result)
    ml_conf   = ml_result.get("confidence", 0.0)

    logger.debug(
        "ML engine → pattern=%s  conf=%.3f",
        ml_result.get("pattern_type"), ml_conf,
    )

    # ── Path B: No rule match at all — use ML only ────────────────────────────
    if rule_conf == 0.0 or rule_result.get("pattern_type") is None:
        logger.debug("PATH B — ML only (rule had no match)")
        return _build_final(
            winner          = ml_result,
            method          = "ml",
            ml_result       = ml_result,
            engines_agreed  = None,
            resolver_path   = "PATH B — ML Only",
            terms           = terms,
        )

    # ── Path D: Both engines agree on pattern ─────────────────────────────────
    rule_pattern = (rule_result.get("pattern_type") or "").lower()
    ml_pattern   = (ml_result.get("pattern_type")   or "").lower()
    engines_agreed = rule_pattern == ml_pattern and bool(rule_pattern)

    if engines_agreed:
        # Use the higher-confidence result as the base, apply agreement bonus
        base    = rule_result if rule_conf >= ml_conf else ml_result
        boosted = min(base["confidence"] + _AGREEMENT_BONUS, 1.0)
        winner  = {**base, "confidence": round(boosted, 6)}

        logger.debug(
            "PATH D — engines agree (pattern=%s)  conf: %.3f → %.3f",
            rule_pattern, base["confidence"], boosted,
        )
        return _build_final(
            winner         = winner,
            method         = "hybrid",
            ml_result      = ml_result,
            engines_agreed = True,
            resolver_path  = "PATH D — Hybrid (both engines agree)",
            terms          = terms,
        )

    # ── Path C: Partial rule match, ML triggered — compare and pick ───────────
    if rule_conf >= _RULE_PARTIAL_THRESHOLD:
        if ml_conf > rule_conf + _ML_OVERRIDE_MARGIN:
            # ML substantially more confident → ML wins with small penalty
            penalised = round(max(ml_conf - _DISAGREEMENT_PENALTY, 0.0), 6)
            winner    = {**ml_result, "confidence": penalised}
            method    = "ml"
            path      = "PATH C — ML override (ML substantially more confident)"
        else:
            # Rule holds, ML partially confirms — hybrid result
            penalised = round(max(rule_conf - _DISAGREEMENT_PENALTY, 0.0), 6)
            winner    = {**rule_result, "confidence": penalised}
            method    = "hybrid"
            path      = "PATH C — Rule confirmed (ML did not override)"

        logger.debug(
            "PATH C — rule=%.3f  ml=%.3f  winner=%s  method=%s",
            rule_conf, ml_conf, winner.get("pattern_type"), method,
        )
        return _build_final(
            winner         = winner,
            method         = method,
            ml_result      = ml_result,
            engines_agreed = False,
            resolver_path  = path,
            terms          = terms,
        )

    # ── Path E: Both low confidence — pick whichever is higher ───────────────
    if ml_conf >= rule_conf:
        penalised = round(max(ml_conf - _DISAGREEMENT_PENALTY, 0.0), 6)
        winner    = {**ml_result, "confidence": penalised}
        method    = "ml"
    else:
        penalised = round(max(rule_conf - _DISAGREEMENT_PENALTY, 0.0), 6)
        winner    = {**rule_result, "confidence": penalised}
        method    = "rule"

    logger.debug(
        "PATH E — low confidence both sides, winner=%s  conf=%.3f",
        winner.get("pattern_type"), penalised,
    )
    return _build_final(
        winner         = winner,
        method         = method,
        ml_result      = ml_result,
        engines_agreed = False,
        resolver_path  = "PATH E — Best available (both low confidence)",
        terms          = terms,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Layer 1 — Rule Engine wrapper
# ─────────────────────────────────────────────────────────────────────────────

def _run_rule_engine(terms: list[float]) -> dict:
    """
    Invoke the rule-based sequence detector.
    Returns a normalised result dict; never raises.
    """
    try:
        from services.rule_engine import detect
        result = detect(terms)
        return _normalise_rule_result(result)
    except ImportError:
        logger.error("sequence_detector module not found — rule engine disabled")
        return _empty_rule_result()
    except Exception as exc:
        logger.error("Rule engine error: %s\n%s", exc, traceback.format_exc())
        return _empty_rule_result()


def _normalise_rule_result(raw: dict | None) -> dict:
    """Ensure the rule engine output has all required keys."""
    if not raw:
        return _empty_rule_result()
    return {
        "pattern_type"  : raw.get("pattern_type"),
        "predicted_next": raw.get("predicted_next"),
        "confidence"    : float(raw.get("confidence", 0.0)),
        "method_used"   : "rule",
        "common_diff"   : raw.get("common_diff"),
        "common_ratio"  : raw.get("common_ratio"),
        "base"          : raw.get("base"),
        "detectors_tried": raw.get("detectors_tried", []),
        "steps"         : raw.get("steps", []),
    }


def _empty_rule_result() -> dict:
    return {
        "pattern_type"  : None,
        "predicted_next": None,
        "confidence"    : 0.0,
        "method_used"   : "rule",
        "common_diff"   : None,
        "common_ratio"  : None,
        "base"          : None,
        "detectors_tried": [],
        "steps"         : [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Layer 2 — ML Engine wrapper
# ─────────────────────────────────────────────────────────────────────────────

def _run_ml_engine(terms: list[float], rule_result: dict) -> dict:
    """
    Invoke the ML model for sequence classification.

    Falls back gracefully if the model is not loaded, or if feature
    engineering fails for any reason.  Never raises.
    """
    # Check whether ML fallback is enabled via settings
    try:
        from database.database import get_setting
        ml_enabled = get_setting("ml_fallback_enabled", True)
        if not ml_enabled:
            logger.debug("ML fallback disabled by settings — returning null ML result")
            return _empty_ml_result("ML fallback disabled in settings.")
    except Exception:
        pass

    # Retrieve the pre-loaded model from the Flask app extension
    loader = _get_model_loader()
    if loader is None:
        logger.warning("ML model not loaded — returning null ML result")
        return _empty_ml_result("Model not loaded. Run training/train_model.py.")

    # Feature engineering
    try:
        from utils.feature_engineering import extract_features
        features = extract_features(terms)
    except Exception as exc:
        logger.error("Feature engineering failed: %s", exc)
        return _empty_ml_result(f"Feature engineering error: {exc}")

    # Inference
    try:
        ml_output  = loader.predict(features)
        pattern    = ml_output.get("pattern_type", "unknown")
        conf       = float(ml_output.get("confidence", _ML_FALLBACK_CONFIDENCE))
        class_prob = ml_output.get("class_probabilities", {})
        top_alt    = ml_output.get("top_alternative", {})
        version    = loader.version or "unknown"
    except Exception as exc:
        logger.error("ML inference error: %s\n%s", exc, traceback.format_exc())
        return _empty_ml_result(f"Inference error: {exc}")

    # Compute actual next_term from the ML-predicted pattern
    next_term = _compute_next_term(pattern, terms, rule_result)

    return {
        "pattern_type"       : pattern,
        "predicted_next"     : next_term,
        "confidence"         : round(conf, 6),
        "method_used"        : "ml",
        "model_version"      : version,
        "class_probabilities": class_prob,
        "top_alternative"    : top_alt,
        "error"              : None,
    }


def _empty_ml_result(reason: str = "") -> dict:
    return {
        "pattern_type"       : "unknown",
        "predicted_next"     : None,
        "confidence"         : _ML_FALLBACK_CONFIDENCE,
        "method_used"        : "ml",
        "model_version"      : "N/A",
        "class_probabilities": {},
        "top_alternative"    : {},
        "error"              : reason,
    }


def _get_model_loader():
    """
    Retrieve the ModelLoader singleton from the Flask app extensions dict.
    Returns None if no app context is available or the model was not loaded.
    """
    try:
        return current_app.extensions.get("model")
    except RuntimeError:
        # No app context (e.g. during unit tests without test client)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Next-term computation
# Translates a pattern label into an actual numeric prediction.
# Called after ML classification so the ML engine always returns a number.
# ─────────────────────────────────────────────────────────────────────────────

def _compute_next_term(
    pattern    : str,
    terms      : list[float],
    rule_result: dict,
) -> float | None:
    """
    Given a predicted pattern type and the input terms, compute the next value.

    For rule-detected patterns this is exact.
    For ML-predicted patterns it uses the best available formula — the same
    formulas the rule engine uses, applied to the ML-classified pattern.
    """
    if not terms:
        return None

    n    = len(terms)
    last = terms[-1]
    prev = terms[-2] if n >= 2 else None

    try:
        p = (pattern or "").lower()

        # ── Arithmetic ────────────────────────────────────────────────────────
        if p == "arithmetic":
            if prev is not None:
                d = last - prev
                return round(last + d, 10)

        # ── Geometric ─────────────────────────────────────────────────────────
        elif p == "geometric":
            if prev is not None and prev != 0:
                r = last / prev
                return round(last * r, 10)

        # ── Fibonacci ─────────────────────────────────────────────────────────
        elif p == "fibonacci":
            if prev is not None:
                return round(last + prev, 10)

        # ── Square ────────────────────────────────────────────────────────────
        elif p == "square":
            start = _find_square_start(terms)
            if start is not None:
                return (start + n) ** 2

        # ── Cube ──────────────────────────────────────────────────────────────
        elif p == "cube":
            start = _find_cube_start(terms)
            if start is not None:
                return (start + n) ** 3

        # ── Triangular ────────────────────────────────────────────────────────
        elif p == "triangular":
            start = _find_triangular_start(terms)
            if start is not None:
                k = start + n
                return k * (k + 1) // 2

        # ── Factorial ─────────────────────────────────────────────────────────
        elif p == "factorial":
            result = _find_factorial_next(terms)
            if result is not None:
                return result

        # ── Prime ─────────────────────────────────────────────────────────────
        elif p == "prime":
            return _next_prime(int(last))

        # ── Power ─────────────────────────────────────────────────────────────
        elif p == "power":
            if prev is not None and prev != 0:
                base = round(last / prev)
                if abs(last / prev - base) < 0.001:
                    return last * base

        # ── Even ──────────────────────────────────────────────────────────────
        elif p == "even":
            if prev is not None:
                return last + (last - prev)

        # ── Odd ───────────────────────────────────────────────────────────────
        elif p == "odd":
            if prev is not None:
                return last + (last - prev)

        # ── Polynomial ────────────────────────────────────────────────────────
        elif p == "polynomial":
            return _extrapolate_polynomial(terms)

        # ── Alternating ───────────────────────────────────────────────────────
        elif p == "alternating":
            return -last

        # ── Increasing / Decreasing ───────────────────────────────────────────
        elif p in ("increasing", "decreasing"):
            if n >= 2:
                diffs   = [terms[i+1] - terms[i] for i in range(n - 1)]
                avg     = sum(diffs) / len(diffs)
                return round(last + avg, 6)

        # ── Unknown ───────────────────────────────────────────────────────────
        # If pattern is unknown or unrecognised, do NOT create fake predictions.
        if p == "unknown" or p is None:
            return None

        # ── Increasing / Decreasing without strict law ────────────────────────
        elif p in ("increasing", "decreasing"):
            return None

    except Exception as exc:
        logger.warning("_compute_next_term error for pattern=%s: %s", pattern, exc)

    return None


def _extrapolate_polynomial(terms: list[float]) -> float:
    """Extrapolate a polynomial sequence of degree len(terms)-1 via Finite Differences."""
    current_diffs = list(terms)
    diff_history = [current_diffs]
    while len(current_diffs) > 1:
        current_diffs = [current_diffs[i+1] - current_diffs[i] for i in range(len(current_diffs) - 1)]
        diff_history.append(current_diffs)
    
    next_diff = diff_history[-1][-1]
    for h in range(len(diff_history) - 2, -1, -1):
        next_diff = diff_history[h][-1] + next_diff
    return float(next_diff)


# ─────────────────────────────────────────────────────────────────────────────
# Mathematical helpers (used by _compute_next_term)
# ─────────────────────────────────────────────────────────────────────────────

_EPS = 1e-6

def _find_square_start(terms: list[float]) -> int | None:
    """Find the starting n such that terms[0] == n²."""
    for s in range(1, 400):
        if abs(terms[0] - s * s) < _EPS:
            # Verify all terms
            if all(abs(terms[i] - (s + i) ** 2) < _EPS for i in range(len(terms))):
                return s
    return None


def _find_cube_start(terms: list[float]) -> int | None:
    """Find the starting n such that terms[0] == n³."""
    for s in range(1, 200):
        if abs(terms[0] - s ** 3) < _EPS:
            if all(abs(terms[i] - (s + i) ** 3) < _EPS for i in range(len(terms))):
                return s
    return None


def _find_triangular_start(terms: list[float]) -> int | None:
    """Find starting n such that terms[0] == n(n+1)/2."""
    for s in range(1, 400):
        if abs(terms[0] - s * (s + 1) / 2) < _EPS:
            if all(abs(terms[i] - (s+i)*(s+i+1)/2) < _EPS for i in range(len(terms))):
                return s
    return None


_FACT_TABLE = [
    1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880,
    3628800, 39916800, 479001600, 6227020800, 87178291200,
    1307674368000, 20922789888000, 355687428096000,
    6402373705728000, 121645100408832000, 2432902008176640000,
]

def _find_factorial_next(terms: list[float]) -> int | None:
    """Return the next factorial after the last term."""
    for start in range(len(_FACT_TABLE)):
        end = start + len(terms)
        if end >= len(_FACT_TABLE):
            break
        if all(abs(terms[i] - _FACT_TABLE[start + i]) < _EPS for i in range(len(terms))):
            return _FACT_TABLE[end]
    return None


def _is_prime(n: int) -> bool:
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for d in range(3, int(n ** 0.5) + 1, 2):
        if n % d == 0:
            return False
    return True


def _next_prime(after: int) -> int:
    """Return the smallest prime strictly greater than after."""
    candidate = after + 1
    while not _is_prime(candidate):
        candidate += 1
    return candidate


# ─────────────────────────────────────────────────────────────────────────────
# Final result assembler
# ─────────────────────────────────────────────────────────────────────────────

def _build_final(
    winner        : dict,
    method        : str,
    ml_result     : dict | None,
    engines_agreed: bool | None,
    resolver_path : str,
    terms         : list[float],
) -> dict:
    """
    Merge winner, ml_result, and metadata into the final prediction dict
    returned to predict_routes.py.
    """
    # Retrieve model version for the meta block
    model_version = "N/A"
    if ml_result and ml_result.get("model_version"):
        model_version = ml_result["model_version"]
    else:
        loader = _get_model_loader()
        if loader and loader.version:
            model_version = loader.version

    # Clamp confidence to [0, 1]
    confidence = max(0.0, min(1.0, winner.get("confidence", 0.0)))

    # If the winner has no predicted_next (edge case), try to compute it
    predicted_next = winner.get("predicted_next")
    if predicted_next is None:
        predicted_next = _compute_next_term(
            winner.get("pattern_type", "unknown"), terms, winner
        )

    return {
        # Core prediction
        "pattern_type"       : winner.get("pattern_type"),
        "predicted_next"     : _safe_number(predicted_next),
        "method_used"        : method,
        "confidence"         : round(confidence, 6),

        # Model metadata
        "model_version"      : model_version,
        "engines_agreed"     : engines_agreed,
        "resolver_path"      : resolver_path,

        # ML detail (empty dicts when ML was not run)
        "class_probabilities": (ml_result or {}).get("class_probabilities", {}),
        "top_alternative"    : (ml_result or {}).get("top_alternative", {}),

        # Raw engine outputs (for engine_trace in the response)
        "rule_result"        : winner if method == "rule" else {},
        "ml_result"          : ml_result or {},

        # Rule engine supplementary fields
        "common_diff"        : winner.get("common_diff"),
        "common_ratio"       : winner.get("common_ratio"),
        "base"               : winner.get("base"),

        # Timestamp
        "predicted_at"       : datetime.now(timezone.utc).isoformat(),
    }


def _safe_number(value: Any) -> float | int | None:
    """
    Convert a numeric value to a JSON-safe Python number.
    Rounds floats that are effectively integers for cleaner display.
    """
    if value is None:
        return None
    try:
        f = float(value)
        # Return as int when the float is a whole number (e.g. 13.0 → 13)
        if f == int(f) and abs(f) < 1e15:
            return int(f)
        # Round to 8 significant decimal places to suppress floating-point noise
        return round(f, 8)
    except (TypeError, ValueError, OverflowError):
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Standalone smoke test (python services/predictor.py)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import os

    # Allow running from the backend/ directory without installing packages
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    test_cases = [
        ([2, 5, 8, 11, 14],      "arithmetic",  17),
        ([3, 6, 12, 24, 48],     "geometric",   96),
        ([1, 1, 2, 3, 5, 8],     "fibonacci",   13),
        ([1, 4, 9, 16, 25],      "square",      36),
        ([1, 8, 27, 64, 125],    "cube",        216),
        ([1, 3, 6, 10, 15],      "triangular",  21),
        ([1, 2, 6, 24, 120],     "factorial",   720),
        ([2, 3, 5, 7, 11, 13],   "prime",       17),
        ([1, 2, 4, 8, 16, 32],   "power",       64),
        ([3, -3, 3, -3, 3],      "alternating", -3),
    ]

    print(f"\n{'Sequence':<30} {'Expected':>12} {'Got':>12} {'Pattern':<14} {'Conf':>6} {'OK?':>5}")
    print("─" * 90)

    passed = 0
    for terms, expected_pattern, expected_next in test_cases:
        # Run just the rule engine for offline testing
        try:
            from services.rule_engine import detect
            raw = detect(terms)
            got_next    = raw.get("predicted_next")
            got_pattern = raw.get("pattern_type", "?")
            conf        = raw.get("confidence", 0.0)
        except ImportError:
            # sequence_detector not yet available — use compute helper directly
            got_next    = _compute_next_term(expected_pattern, terms, {})
            got_pattern = expected_pattern
            conf        = 1.0

        ok = (
            got_pattern == expected_pattern
            and got_next is not None
            and abs(float(got_next) - expected_next) < 0.01
        )
        passed += ok
        seq_str = str(terms[:5])[:-1] + "…]" if len(terms) > 5 else str(terms)
        print(
            f"{seq_str:<30} {expected_next:>12} {str(got_next):>12} "
            f"{got_pattern:<14} {conf:>6.2f} {'✓' if ok else '✗':>5}"
        )

    print(f"\n{passed}/{len(test_cases)} tests passed.")