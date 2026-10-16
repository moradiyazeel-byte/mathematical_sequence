"""
services/rule_engine.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Deterministic Rule Engine

Contains Python implementations of detectors for:
    - Arithmetic, Geometric, Prime, Square, Cube, Even, Odd,
      Factorial, Triangular, Power, Alternating, Polynomial,
      Increasing, Decreasing.
──────────────────────────────────────────────────────────────────────────────
"""

import math
from typing import Any, Dict, List, Optional

_EPS = 1e-4  # floating-point tolerance for differences/ratios


def _all_close(values: List[float], eps: float = _EPS) -> bool:
    """Check if all values are within eps of the first element."""
    if len(values) < 2:
        return False
    return all(abs(v - values[0]) <= eps for v in values)


def _is_prime(x: float) -> bool:
    """Verify whether a float value is prime."""
    if not x.is_integer() or x < 2:
        return False
    val = int(x)
    if val == 2:
        return True
    if val % 2 == 0:
        return False
    for d in range(3, int(val ** 0.5) + 1, 2):
        if val % d == 0:
            return False
    return True


def _next_prime(x: float) -> int:
    """Find the smallest prime strictly greater than x."""
    val = int(x)
    n = val + 1
    while not _is_prime(float(n)):
        n += 1
    return n


def _detect_arithmetic(terms: List[float]) -> Optional[Dict[str, Any]]:
    d = [terms[i+1] - terms[i] for i in range(len(terms)-1)]
    if d and _all_close(d):
        return {
            "pattern_type": "arithmetic",
            "predicted_next": terms[-1] + d[0],
            "confidence": 1.0,
            "common_diff": d[0]
        }
    return None


def _detect_geometric(terms: List[float]) -> Optional[Dict[str, Any]]:
    if any(abs(t) <= _EPS for t in terms):
        return None
    r = [terms[i+1] / terms[i] for i in range(len(terms)-1)]
    if r and _all_close(r):
        return {
            "pattern_type": "geometric",
            "predicted_next": terms[-1] * r[0],
            "confidence": 1.0,
            "common_ratio": r[0]
        }
    return None


def _detect_prime_modified(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    # All terms must be integers
    if not all(Number.is_integer(t) for t in terms):
        return None
    
    # Calculate differences
    diffs = [int(terms[i+1] - terms[i]) for i in range(len(terms)-1)]
    
    # Generate primes up to say 2000
    max_limit = 2000
    primes = []
    curr = 2
    while len(primes) < max_limit:
        if _is_prime(float(curr)):
            primes.append(curr)
        curr += 1
        
    # Find consecutive primes matching diffs
    best_match = None
    
    for start_idx in range(len(primes) - len(terms)):
        match = True
        for j in range(len(diffs)):
            if primes[start_idx + j + 1] - primes[start_idx + j] != diffs[j]:
                match = False
                break
        if match:
            offset = int(terms[0]) - primes[start_idx]
            if all(int(terms[j]) == primes[start_idx + j] + offset for j in range(len(terms))):
                if offset == 0:
                    best_match = (offset, primes[start_idx + len(terms)])
                    break
                elif best_match is None:
                    best_match = (offset, primes[start_idx + len(terms)])
                    
    if best_match is not None:
        matched_offset, next_prime_val = best_match
        return {
            "pattern_type": "prime",
            "predicted_next": float(next_prime_val + matched_offset),
            "confidence": 0.98
        }
    return None


def _detect_square(terms: List[float]) -> Optional[Dict[str, Any]]:
    if any(t < 0 for t in terms):
        return None
    start = -1
    for s in range(1, 301):
        if abs(terms[0] - s * s) < _EPS:
            start = s
            break
    if start >= 1:
        if all(abs(terms[i] - (start + i) ** 2) < _EPS for i in range(len(terms))):
            return {
                "pattern_type": "square",
                "predicted_next": float((start + len(terms)) ** 2),
                "confidence": 1.0,
                "base": start
            }
    return None


def _detect_cube(terms: List[float]) -> Optional[Dict[str, Any]]:
    start = -1
    for s in range(1, 201):
        if abs(terms[0] - s ** 3) < _EPS:
            start = s
            break
    if start >= 1:
        if all(abs(terms[i] - (start + i) ** 3) < _EPS for i in range(len(terms))):
            return {
                "pattern_type": "cube",
                "predicted_next": float((start + len(terms)) ** 3),
                "confidence": 1.0,
                "base": start
            }
    return None


def _detect_even(terms: List[float]) -> Optional[Dict[str, Any]]:
    if not all(t.is_integer() and int(t) % 2 == 0 for t in terms):
        return None
    d = [terms[i+1] - terms[i] for i in range(len(terms)-1)]
    if d and _all_close(d):
        return {
            "pattern_type": "even",
            "predicted_next": terms[-1] + d[0],
            "confidence": 0.90,
            "common_diff": d[0]
        }
    return None


def _detect_odd(terms: List[float]) -> Optional[Dict[str, Any]]:
    if not all(t.is_integer() and abs(int(t)) % 2 == 1 for t in terms):
        return None
    d = [terms[i+1] - terms[i] for i in range(len(terms)-1)]
    if d and _all_close(d):
        return {
            "pattern_type": "odd",
            "predicted_next": terms[-1] + d[0],
            "confidence": 0.90,
            "common_diff": d[0]
        }
    return None


_FACT_TABLE = [
    1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880,
    3628800, 39916800, 479001600, 6227020800, 87178291200,
    1307674368000, 20922789888000, 355687428096000,
    6402373705728000, 121645100408832000, 2432902008176640000
]


def _detect_factorial_modified(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    for start in range(1, 12):
        f = []
        for i in range(len(terms) + 1):
            f.append(float(math.factorial(start + i)))
            
        denom = f[1] - f[0]
        if abs(denom) > _EPS:
            M = (terms[1] - terms[0]) / denom
            C = terms[0] - M * f[0]
            if all(abs(terms[i] - (M * f[i] + C)) < _EPS for i in range(len(terms))):
                if abs(M - round(M)) < 1e-4: M = round(M)
                if abs(C - round(C)) < 1e-4: C = round(C)
                return {
                    "pattern_type": "factorial",
                    "predicted_next": float(M * f[-1] + C),
                    "confidence": 0.98,
                    "base": start
                }
    return None


def _detect_triangular_modified(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    def tri(k: int) -> int:
        return k * (k + 1) // 2
        
    for start in range(1, 100):
        t = [float(tri(start + i)) for i in range(len(terms) + 1)]
        denom = t[1] - t[0]
        if abs(denom) > _EPS:
            M = (terms[1] - terms[0]) / denom
            C = terms[0] - M * t[0]
            if all(abs(terms[i] - (M * t[i] + C)) < _EPS for i in range(len(terms))):
                if abs(M - round(M)) < 1e-4: M = round(M)
                if abs(C - round(C)) < 1e-4: C = round(C)
                return {
                    "pattern_type": "triangular",
                    "predicted_next": float(M * t[-1] + C),
                    "confidence": 0.98,
                    "base": start
                }
    return None


def _detect_power_modified(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    for base in [2, 3, 5, 10]:
        for start in range(0, 12):
            p = [float(base ** (start + i)) for i in range(len(terms) + 1)]
            denom = p[1] - p[0]
            if abs(denom) > _EPS:
                M = (terms[1] - terms[0]) / denom
                C = terms[0] - M * p[0]
                if all(abs(terms[i] - (M * p[i] + C)) < _EPS for i in range(len(terms))):
                    if abs(M - round(M)) < 1e-4: M = round(M)
                    if abs(C - round(C)) < 1e-4: C = round(C)
                    return {
                        "pattern_type": "power",
                        "predicted_next": float(M * p[-1] + C),
                        "confidence": 0.98,
                        "base": base
                    }
    return None


def _detect_periodic_step(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 5:
        return None
        
    # Case 1: alternating add and multiply (add first)
    d = terms[1] - terms[0]
    if abs(terms[1]) > _EPS:
        r = terms[2] / terms[1]
        match = True
        for i in range(1, len(terms)):
            if i % 2 == 1:
                if abs(terms[i] - (terms[i-1] + d)) > _EPS:
                    match = False
                    break
            else:
                if abs(terms[i] - (terms[i-1] * r)) > _EPS:
                    match = False
                    break
        if match:
            next_idx = len(terms)
            next_val = terms[-1] + d if next_idx % 2 == 1 else terms[-1] * r
            return {
                "pattern_type": "custom",
                "predicted_next": float(next_val),
                "confidence": 0.98,
                "description": f"Periodic add ({d}) and multiply ({r})"
            }

    # Case 2: alternating multiply and add (multiply first)
    if abs(terms[0]) > _EPS:
        r = terms[1] / terms[0]
        d = terms[2] - terms[1]
        match = True
        for i in range(1, len(terms)):
            if i % 2 == 1:
                if abs(terms[i] - (terms[i-1] * r)) > _EPS:
                    match = False
                    break
            else:
                if abs(terms[i] - (terms[i-1] + d)) > _EPS:
                    match = False
                    break
        if match:
            next_idx = len(terms)
            next_val = terms[-1] * r if next_idx % 2 == 1 else terms[-1] + d
            return {
                "pattern_type": "custom",
                "predicted_next": float(next_val),
                "confidence": 0.98,
                "description": f"Periodic multiply ({r}) and add ({d})"
            }

    # Case 3: periodic differences (add, add)
    d0 = terms[1] - terms[0]
    d1 = terms[2] - terms[1]
    match = True
    for i in range(1, len(terms)):
        expected_diff = d0 if i % 2 == 1 else d1
        if abs((terms[i] - terms[i-1]) - expected_diff) > _EPS:
            match = False
            break
    if match:
        next_idx = len(terms)
        next_val = terms[-1] + d0 if next_idx % 2 == 1 else terms[-1] + d1
        return {
            "pattern_type": "custom",
            "predicted_next": float(next_val),
            "confidence": 0.98,
            "description": f"Periodic difference step ({d0}, {d1})"
        }

    # Case 4: periodic ratios (multiply, multiply)
    if abs(terms[0]) > _EPS and abs(terms[1]) > _EPS:
        r0 = terms[1] / terms[0]
        r1 = terms[2] / terms[1]
        if not any(abs(t) <= _EPS for t in terms):
            match = True
            for i in range(1, len(terms)):
                expected_ratio = r0 if i % 2 == 1 else r1
                if abs((terms[i] / terms[i-1]) - expected_ratio) > _EPS:
                    match = False
                    break
            if match:
                next_idx = len(terms)
                next_val = terms[-1] * r0 if next_idx % 2 == 1 else terms[-1] * r1
                return {
                    "pattern_type": "custom",
                    "predicted_next": float(next_val),
                    "confidence": 0.98,
                    "description": f"Periodic ratio step ({r0}, {r1})"
                }

    return None


def _detect_fibonacci(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 4:
        return None
    if all(abs(terms[i] - (terms[i-1] + terms[i-2])) < _EPS for i in range(2, len(terms))):
        return {
            "pattern_type": "fibonacci",
            "predicted_next": terms[-1] + terms[-2],
            "confidence": 0.98
        }
    x0, x1, x2, x3 = terms[0], terms[1], terms[2], terms[3]
    det = x1 * x1 - x0 * x2
    if abs(det) > 1e-5:
        c1 = (x2 * x1 - x0 * x3) / det
        c2 = (x1 * x3 - x2 * x2) / det
        # Enforce that c1 and c2 must be integers or very close to integers
        if abs(c1 - round(c1)) < 1e-4 and abs(c2 - round(c2)) < 1e-4:
            c1 = round(c1)
            c2 = round(c2)
            if all(abs(terms[i] - (c1 * terms[i-1] + c2 * terms[i-2])) < _EPS for i in range(2, len(terms))):
                return {
                    "pattern_type": "custom" if (c1 != 1 or c2 != 1) else "fibonacci",
                    "predicted_next": float(c1 * terms[-1] + c2 * terms[-2]),
                    "confidence": 0.95,
                    "c1": c1,
                    "c2": c2
                }
    return None


def _detect_tribonacci(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 4:
        return None
    if all(abs(terms[i] - (terms[i-1] + terms[i-2] + terms[i-3])) < _EPS for i in range(3, len(terms))):
        return {
            "pattern_type": "tribonacci",
            "predicted_next": terms[-1] + terms[-2] + terms[-3],
            "confidence": 0.98
        }
    return None


def _detect_padovan(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 4:
        return None
    if all(abs(terms[i] - (terms[i-2] + terms[i-3])) < _EPS for i in range(3, len(terms))):
        return {
            "pattern_type": "padovan",
            "predicted_next": terms[-2] + terms[-3],
            "confidence": 0.98
        }
    return None


_CATALAN_TABLE = [
    1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796, 58786, 208012,
    742900, 2674440, 9694845, 35357670, 129644790, 477638700, 1767263190
]


def _detect_catalan(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    for start in range(len(_CATALAN_TABLE)):
        end = start + len(terms)
        if end >= len(_CATALAN_TABLE):
            break
        if all(abs(terms[i] - _CATALAN_TABLE[start + i]) < _EPS for i in range(len(terms))):
            return {
                "pattern_type": "catalan",
                "predicted_next": float(_CATALAN_TABLE[end]),
                "confidence": 0.98,
                "base": start
            }
    return None


def _detect_alternating(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None

    # Case 1: Alternating Value Cycle (e.g., 1, 3, 1, 3, 1 or 4, 7, 4, 7, 4 or 10, 20, 10, 20)
    if all(abs(terms[i] - terms[i - 2]) <= _EPS for i in range(2, len(terms))):
        return {
            "pattern_type": "alternating",
            "predicted_next": terms[-2],
            "confidence": 0.99,
            "period": 2,
            "cycle_values": [terms[-2], terms[-1]]
        }

    # Case 2: Periodic Cycle (e.g., 1, 2, 3, 1, 2, 3)
    for period in [3, 4]:
        if len(terms) >= period * 2 - 1:
            if all(abs(terms[i] - terms[i - period]) <= _EPS for i in range(period, len(terms))):
                return {
                    "pattern_type": "periodic_step",
                    "predicted_next": terms[-period],
                    "confidence": 0.98,
                    "period": period
                }

    # Case 3: Alternating Signs (+ and -) (e.g., 1, -1, 1, -1, 1 or 2, -4, 6, -8, 10)
    def _sign(val):
        return 1 if val > 0 else (-1 if val < 0 else 0)

    signs_alternate = all(_sign(terms[i]) != _sign(terms[i-1]) and terms[i] != 0 for i in range(1, len(terms)))
    if signs_alternate:
        abs_terms = [abs(t) for t in terms]
        abs_detectors = [
            ("arithmetic",  _detect_arithmetic),
            ("geometric",   _detect_geometric),
            ("square",      _detect_square),
            ("cube",        _detect_cube),
            ("power",       _detect_power_modified),
        ]
        for name, detector_fn in abs_detectors:
            try:
                res = detector_fn(abs_terms)
                if res is not None and res.get("predicted_next") is not None:
                    next_sign = -1 if terms[-1] > 0 else 1
                    return {
                        "pattern_type": "alternating",
                        "predicted_next": res["predicted_next"] * next_sign,
                        "confidence": 0.95,
                        "base_pattern": res["pattern_type"]
                    }
            except Exception:
                pass

        if _all_close(abs_terms):
            return {
                "pattern_type": "alternating",
                "predicted_next": -terms[-1],
                "confidence": 0.98
            }

    return None


def _detect_polynomial(terms: List[float]) -> Optional[Dict[str, Any]]:
    n = len(terms)
    if n < 3:
        return None

    current_diffs = list(terms)
    diff_history = [current_diffs]

    for k in range(1, n - 1):
        current_diffs = [current_diffs[i+1] - current_diffs[i] for i in range(len(current_diffs) - 1)]
        diff_history.append(current_diffs)

        if len(current_diffs) >= 2 and _all_close(current_diffs):
            const_val = current_diffs[0]
            next_diff = const_val
            for h in range(k - 1, -1, -1):
                next_diff = diff_history[h][-1] + next_diff

            return {
                "pattern_type": "polynomial",
                "predicted_next": next_diff,
                "confidence": 0.98,
                "degree": k
            }
    return None


def _detect_difference_geometric(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 4:
        return None
        
    current_diffs = list(terms)
    diff_history = [current_diffs]
    
    for order in range(1, 4):
        current_diffs = [current_diffs[i+1] - current_diffs[i] for i in range(len(current_diffs) - 1)]
        diff_history.append(current_diffs)
        
        if len(current_diffs) >= 3:
            if not any(abs(x) <= _EPS for x in current_diffs):
                r = [current_diffs[i+1] / current_diffs[i] for i in range(len(current_diffs)-1)]
                if r and _all_close(r):
                    next_diff_val = current_diffs[-1] * r[0]
                    curr_val = next_diff_val
                    for h in range(order - 1, -1, -1):
                        curr_val = diff_history[h][-1] + curr_val
                        
                    return {
                        "pattern_type": "power",
                        "predicted_next": curr_val,
                        "confidence": 0.95,
                        "diff_order": order,
                        "ratio": r[0]
                    }
    return None


def _detect_increasing(terms: List[float]) -> Optional[Dict[str, Any]]:
    d = [terms[i+1] - terms[i] for i in range(len(terms)-1)]
    if all(v > 0 for v in d):
        avg = sum(d) / len(d)
        return {
            "pattern_type": "increasing",
            "predicted_next": terms[-1] + avg,
            "confidence": 0.60
        }
    return None


def _detect_decreasing(terms: List[float]) -> Optional[Dict[str, Any]]:
    d = [terms[i+1] - terms[i] for i in range(len(terms)-1)]
    if all(v < 0 for v in d):
        avg = sum(d) / len(d)
        return {
            "pattern_type": "decreasing",
            "predicted_next": terms[-1] + avg,
            "confidence": 0.60
        }
    return None


# Helper to enable calling the standard isinstance(x, int) checks in _detect_prime
class Number:

    @staticmethod
    def is_integer(val: float) -> bool:
        try:
            return val.is_integer()
        except AttributeError:
            return isinstance(val, int)


def _detect_lucas(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    if not all(Number.is_integer(t) for t in terms):
        return None
    lucas_table = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322, 521, 843, 1364, 2207, 3571, 5778, 9349, 15127]
    for start in range(len(lucas_table) - len(terms)):
        if all(abs(terms[i] - lucas_table[start + i]) < _EPS for i in range(len(terms))):
            return {
                "pattern_type": "lucas",
                "predicted_next": float(lucas_table[start + len(terms)]),
                "confidence": 0.98,
                "base": start
            }
    return None


def _detect_pell(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    if not all(Number.is_integer(t) for t in terms):
        return None
    if all(abs(terms[i] - (2 * terms[i-1] + terms[i-2])) < _EPS for i in range(2, len(terms))):
        pell_table = [0, 1, 2, 5, 12, 29, 70, 169, 408, 985, 2378, 5741, 13860, 33461]
        for start in range(len(pell_table) - len(terms)):
            if all(abs(terms[i] - pell_table[start + i]) < _EPS for i in range(len(terms))):
                return {
                    "pattern_type": "pell",
                    "predicted_next": float(pell_table[start + len(terms)]),
                    "confidence": 0.98,
                    "base": start
                }
        return {
            "pattern_type": "pell",
            "predicted_next": float(2 * terms[-1] + terms[-2]),
            "confidence": 0.95
        }
    return None


def _detect_jacobsthal(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    if not all(Number.is_integer(t) for t in terms):
        return None
    if all(abs(terms[i] - (terms[i-1] + 2 * terms[i-2])) < _EPS for i in range(2, len(terms))):
        jacob_table = [0, 1, 1, 3, 5, 11, 21, 43, 85, 171, 341, 683, 1365, 2731, 5461, 10923]
        for start in range(len(jacob_table) - len(terms)):
            if all(abs(terms[i] - jacob_table[start + i]) < _EPS for i in range(len(terms))):
                return {
                    "pattern_type": "jacobsthal",
                    "predicted_next": float(jacob_table[start + len(terms)]),
                    "confidence": 0.98,
                    "base": start
                }
        return {
            "pattern_type": "jacobsthal",
            "predicted_next": float(terms[-1] + 2 * terms[-2]),
            "confidence": 0.95
        }
    return None


def _detect_collatz(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    if not all(Number.is_integer(t) and t > 0 for t in terms):
        return None
    for i in range(len(terms) - 1):
        prev = int(terms[i])
        curr = int(terms[i+1])
        if prev % 2 == 0:
            if curr != prev // 2:
                return None
        else:
            if curr != 3 * prev + 1:
                return None
    last = int(terms[-1])
    next_val = last // 2 if last % 2 == 0 else 3 * last + 1
    return {
        "pattern_type": "collatz",
        "predicted_next": float(next_val),
        "confidence": 0.98
    }


def _detect_look_and_say(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 2:
        return None
    if not all(Number.is_integer(t) and t > 0 for t in terms):
        return None
        
    def next_look_and_say(val_str: str) -> str:
        if not val_str:
            return ""
        result = []
        count = 1
        curr_char = val_str[0]
        for c in val_str[1:]:
            if c == curr_char:
                count += 1
            else:
                result.append(f"{count}{curr_char}")
                count = 1
                curr_char = c
        result.append(f"{count}{curr_char}")
        return "".join(result)

    for i in range(len(terms) - 1):
        prev_str = str(int(terms[i]))
        curr_str = str(int(terms[i+1]))
        if next_look_and_say(prev_str) != curr_str:
            return None
            
    last_str = str(int(terms[-1]))
    next_str = next_look_and_say(last_str)
    try:
        predicted = float(next_str)
        return {
            "pattern_type": "look_and_say",
            "predicted_next": predicted,
            "confidence": 0.98
        }
    except ValueError:
        return None


def _detect_pentagonal(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    for start in range(1, 200):
        expected = [((start+i)*(3*(start+i)-1))//2 for i in range(len(terms))]
        if all(abs(terms[i] - expected[i]) < _EPS for i in range(len(terms))):
            next_n = start + len(terms)
            return {
                "pattern_type": "pentagonal",
                "predicted_next": float((next_n * (3 * next_n - 1)) // 2),
                "confidence": 1.0,
                "base": start
            }
    return None


def _detect_hexagonal(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    for start in range(1, 200):
        expected = [(start+i)*(2*(start+i)-1) for i in range(len(terms))]
        if all(abs(terms[i] - expected[i]) < _EPS for i in range(len(terms))):
            next_n = start + len(terms)
            return {
                "pattern_type": "hexagonal",
                "predicted_next": float(next_n * (2 * next_n - 1)),
                "confidence": 1.0,
                "base": start
            }
    return None


def _detect_oblong(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    for start in range(1, 200):
        expected = [(start+i)*(start+i+1) for i in range(len(terms))]
        if all(abs(terms[i] - expected[i]) < _EPS for i in range(len(terms))):
            next_n = start + len(terms)
            return {
                "pattern_type": "oblong",
                "predicted_next": float(next_n * (next_n + 1)),
                "confidence": 1.0,
                "base": start
            }
    return None


def _detect_sum_of_squares(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    for start in range(1, 200):
        expected = [((start+i)*(start+i+1)*(2*(start+i)+1))//6 for i in range(len(terms))]
        if all(abs(terms[i] - expected[i]) < _EPS for i in range(len(terms))):
            next_n = start + len(terms)
            return {
                "pattern_type": "sum_of_squares",
                "predicted_next": float((next_n * (next_n + 1) * (2 * next_n + 1)) // 6),
                "confidence": 1.0,
                "base": start
            }
    return None


def _detect_sum_of_cubes(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    for start in range(1, 200):
        expected = [((start+i)*(start+i+1)//2)**2 for i in range(len(terms))]
        if all(abs(terms[i] - expected[i]) < _EPS for i in range(len(terms))):
            next_n = start + len(terms)
            return {
                "pattern_type": "sum_of_cubes",
                "predicted_next": float(((next_n * (next_n + 1)) // 2) ** 2),
                "confidence": 1.0,
                "base": start
            }
    return None


def _detect_mersenne(terms: List[float]) -> Optional[Dict[str, Any]]:
    if len(terms) < 3:
        return None
    for start in range(0, 50):
        expected = [2**(start+i)-1 for i in range(len(terms))]
        if all(abs(terms[i] - expected[i]) < _EPS for i in range(len(terms))):
            next_n = start + len(terms)
            return {
                "pattern_type": "mersenne",
                "predicted_next": float(2**next_n - 1),
                "confidence": 1.0,
                "base": start
            }
    return None


# ── Orchestrator ──

def detect(terms: List[float]) -> dict:
    """
    Evaluate a sequence against the priority rule detectors.
    """
    detectors = [
        ("collatz",     _detect_collatz),
        ("look_and_say", _detect_look_and_say),
        ("lucas",       _detect_lucas),
        ("pell",        _detect_pell),
        ("jacobsthal",  _detect_jacobsthal),
        ("pentagonal",  _detect_pentagonal),
        ("hexagonal",   _detect_hexagonal),
        ("oblong",      _detect_oblong),
        ("sum_of_squares", _detect_sum_of_squares),
        ("sum_of_cubes", _detect_sum_of_cubes),
        ("mersenne",    _detect_mersenne),
        ("arithmetic",  _detect_arithmetic),
        ("geometric",   _detect_geometric),
        ("prime",       _detect_prime_modified),
        ("fibonacci",   _detect_fibonacci),
        ("tribonacci",  _detect_tribonacci),
        ("padovan",     _detect_padovan),
        ("catalan",     _detect_catalan),
        ("periodic_step", _detect_periodic_step),
        ("square",      _detect_square),
        ("cube",        _detect_cube),
        ("triangular",  _detect_triangular_modified),
        ("factorial",   _detect_factorial_modified),
        ("power",       _detect_power_modified),
        ("even",        _detect_even),
        ("odd",         _detect_odd),
        ("alternating", _detect_alternating),
        ("polynomial",  _detect_polynomial),
        ("diff_geom",   _detect_difference_geometric),
        ("increasing",  _detect_increasing),
        ("decreasing",  _detect_decreasing),
    ]

    tried = []
    for name, detector_fn in detectors:
        tried.append(name)
        try:
            res = detector_fn(terms)
            if res is not None:
                res["detectors_tried"] = tried
                return res
        except Exception:
            pass

    # Fallback for unknown/custom sequences: compute trend & finite difference prediction
    if len(terms) >= 2:
        diffs = [terms[i+1] - terms[i] for i in range(len(terms)-1)]
        avg_diff = sum(diffs) / len(diffs)
        pred_next = round(terms[-1] + avg_diff, 6)
    else:
        pred_next = terms[-1] if terms else None

    return {
        "pattern_type": "unknown",
        "predicted_next": pred_next,
        "confidence": 0.45,
        "detectors_tried": tried,
    }
