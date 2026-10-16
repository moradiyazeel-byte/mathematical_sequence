"""
utils/preprocessing.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Preprocessing Utilities

Functions for parsing and validating raw sequence inputs.
──────────────────────────────────────────────────────────────────────────────
"""

import math
from typing import Any


def parse_and_validate(
    raw: Any,
    min_terms: int = 3,
    max_terms: int = 50,
) -> tuple[list[float] | None, str | None]:
    """
    Parse a raw input sequence (JSON array, comma-separated string, etc.)
    and validate it against structural requirements.

    Parameters
    ----------
    raw : Any
        A list of floats, or a comma/semicolon-separated string.
    min_terms : int
        Minimum number of terms required.
    max_terms : int
        Maximum number of terms accepted.

    Returns
    -------
    tuple (terms, error_msg)
        On success: (list of floats, None)
        On failure: (None, error_msg string)
    """
    if raw is None:
        return None, "Sequence input is missing or empty."

    # Parse string input
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
        return None, "Sequence must be a list or comma-separated string."

    # Validate term counts
    n = len(terms)
    if n < min_terms:
        return None, f"Minimum {min_terms} terms required. You provided {n}."
    if n > max_terms:
        return None, f"Maximum {max_terms} terms accepted. You provided {n}."

    # Validate finite values (no NaN, Inf)
    for idx, t in enumerate(terms):
        if math.isnan(t) or math.isinf(t):
            return None, f"Sequence contains non-finite term at index {idx} (NaN or Infinity)."

    return terms, None
