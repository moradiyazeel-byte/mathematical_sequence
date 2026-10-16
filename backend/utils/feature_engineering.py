"""
utils/feature_engineering.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Feature Engineering Utilities

Responsible for transforming a list of sequence terms into the 53-dimensional
numeric feature vector expected by the Random Forest classifier.
──────────────────────────────────────────────────────────────────────────────
"""

import math
import numpy as np

_GOLDEN_RATIO = (1 + math.sqrt(5)) / 2


def _safe_div(a: float, b: float, default: float = 0.0) -> float:
    """Division with zero-guard."""
    return a / b if abs(b) > 1e-10 else default


def _all_close(values: list[float], eps: float = 0.001) -> bool:
    """Check if all values are within epsilon of the first element."""
    if len(values) < 2:
        return False
    return all(abs(v - values[0]) <= eps for v in values)


def extract_features(terms: list[float]) -> np.ndarray:
    """
    Transform a raw list of sequence terms into a 53-dimensional numeric
    feature vector for machine learning inference.

    Features generated must match training/train_model.py exactly.
    Slices the terms list to the first 8 terms to be consistent with
    model training window size.

    Parameters
    ----------
    terms : list of floats

    Returns
    -------
    np.ndarray
        2D array of shape (1, 53) containing engineered features.
    """
    # Slice to model window (first 8 terms) and pad if less than 3
    terms_window = [float(v) for v in terms[:8]]
    if len(terms_window) < 3:
        terms_window = terms_window + [0.0] * (3 - len(terms_window))
    
    n = len(terms_window)
    feats = []

    # ── Group A: Differences ──────────────────────────────────────────────
    d1 = [terms_window[i+1] - terms_window[i] for i in range(n-1)]
    d2 = [d1[i+1] - d1[i]                     for i in range(len(d1)-1)]
    d3 = [d2[i+1] - d2[i]                     for i in range(len(d2)-1)]

    def _pad(lst, length, fill=0.0):
        return lst[:length] + [fill] * max(0, length - len(lst))

    feats += _pad(d1, 7)    # 7 features
    feats += _pad(d2, 7)    # 7 features
    feats += _pad(d3, 5)    # 5 features

    # ── Group B: Ratios ───────────────────────────────────────────────────
    ratios = [_safe_div(terms_window[i+1], terms_window[i]) for i in range(n-1)]
    feats += _pad(ratios, 7)    # 7 features

    # ── Group C: Statistics ───────────────────────────────────────────────
    mean_val = float(np.mean(terms_window))
    std_val  = float(np.std(terms_window)) if n > 1 else 0.0
    min_val  = float(np.min(terms_window))
    max_val  = float(np.max(terms_window))
    range_v  = max_val - min_val
    if std_val > 1e-10 and n > 2:
        skew = float(np.mean([(t - mean_val)**3 for t in terms_window]) / std_val**3)
    else:
        skew = 0.0
    feats += [mean_val, std_val, min_val, max_val, range_v, skew]   # 6

    # ── Group D: Pattern-hint boolean flags ───────────────────────────────
    flag_arith  = 1.0 if d1 and _all_close(d1) else 0.0
    flag_geom   = 1.0 if ratios and _all_close(ratios) else 0.0
    flag_exp    = 1.0 if flag_geom and ratios and abs(ratios[0]) > 1.01 else 0.0
    flag_poly   = 1.0 if d2 and _all_close(d2) else 0.0
    flag_golden = 1.0 if ratios and any(abs(r - _GOLDEN_RATIO) < 0.05 for r in ratios) else 0.0
    flag_pos    = 1.0 if all(t > 0 for t in terms_window) else 0.0
    flag_int    = 1.0 if all(float(t) == int(t) for t in terms_window) else 0.0
    flag_alt    = 1.0 if n > 1 and all(
        math.copysign(1, terms_window[i]) != math.copysign(1, terms_window[i+1])
        for i in range(n-1)
    ) else 0.0

    feats += [flag_arith, flag_geom, flag_exp, flag_poly,
              flag_golden, flag_pos, flag_int, flag_alt]    # 8

    # ── Group E: Identity features ────────────────────────────────────────
    feats += [
        float(n),                          # sequence length used
        float(terms_window[0]),            # first term
        float(terms_window[-1]),           # last term
        float(sum(terms_window)),          # sum
        float(sum(terms_window[:3])),      # sum of first 3
    ]   # 5

    # ── Group F: Scalar summaries ─────────────────────────────────────────
    mean_d1     = float(np.mean(d1)) if d1 else 0.0
    std_d1      = float(np.std(d1)) if d1 else 0.0
    mean_ratio  = float(np.mean(ratios)) if ratios else 0.0
    std_ratio   = float(np.std(ratios)) if ratios else 0.0
    mean_d2     = float(np.mean(d2)) if d2 else 0.0
    growth_rate = _safe_div(terms_window[-1] - terms_window[0], float(n - 1)) if n > 1 else 0.0

    feats += [mean_d1, std_d1, mean_ratio, std_ratio, mean_d2, growth_rate]  # 6

    # Clean up NaN / Inf values in case of division noise
    feats = [0.0 if (math.isnan(v) or math.isinf(v)) else v for v in feats]

    return np.array([feats], dtype=np.float64)


def build_explanation(result: dict, terms: list[float]) -> dict:
    """
    Placeholder explanation builder.
    Note: The actual calculation text is built by predict_routes.py.
    """
    return {}
