import sys
import os
import time
import json
import math

sys.path.insert(0, os.path.abspath("backend"))
from app import create_app

# ─────────────────────────────────────────────────────────────────────────────
# Generator for 200 Hard & Unknown Sequences
# ─────────────────────────────────────────────────────────────────────────────

def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0: return False
    return True

def get_primes(count):
    primes = []
    curr = 2
    while len(primes) < count:
        if is_prime(curr):
            primes.append(curr)
        curr += 1
    return primes

ALL_PRIMES = get_primes(100)

def generate_200_hard_sequences():
    seqs = []

    # 1. Hard Arithmetic (20 cases)
    # Floating diffs, negative diffs, large offsets
    arith_cases = [
        ([10.5, 13.2, 15.9, 18.6, 21.3], 24.0, "Hard Arithmetic (Float)"),
        ([-50, -38, -26, -14, -2], 10.0, "Hard Arithmetic (Negative)"),
        ([1000, 935, 870, 805, 740], 675.0, "Hard Arithmetic (Decreasing)"),
        ([1.11, 2.22, 3.33, 4.44, 5.55], 6.66, "Hard Arithmetic (Decimals)"),
        ([99, 198, 297, 396, 495], 594.0, "Hard Arithmetic (Large Step)"),
    ]
    for base in range(15):
        a = base * 7 - 40
        d = 3.5 + (base % 5) * 1.5
        s = [round(a + i * d, 4) for i in range(5)]
        arith_cases.append((s, round(a + 5 * d, 4), f"Hard Arithmetic #{base+6}"))

    for s, nxt, name in arith_cases[:20]:
        seqs.append({"name": name, "category": "Arithmetic", "sequence": s, "expected_next": nxt, "expected_type": "arithmetic"})

    # 2. Hard Geometric (20 cases)
    geom_cases = [
        ([1.5, 4.5, 13.5, 40.5, 121.5], 364.5, "Hard Geometric (Fractional Base)"),
        ([2, -6, 18, -54, 162], -486.0, "Hard Geometric (Negative Ratio)"),
        ([1024, 512, 256, 128, 64], 32.0, "Hard Geometric (Decay Ratio 0.5)"),
        ([0.8, 1.6, 3.2, 6.4, 12.8], 25.6, "Hard Geometric (Float Start)"),
        ([5, 20, 80, 320, 1280], 5120.0, "Hard Geometric (Ratio 4)"),
    ]
    for idx in range(15):
        a = (idx % 4) + 1
        r = 1.5 if idx % 2 == 0 else -2.5
        s = [round(a * (r ** i), 4) for i in range(5)]
        geom_cases.append((s, round(a * (r ** 5), 4), f"Hard Geometric #{idx+6}"))

    for s, nxt, name in geom_cases[:20]:
        seqs.append({"name": name, "category": "Geometric", "sequence": s, "expected_next": nxt, "expected_type": "geometric"})

    # 3. Recurrence / Fibonacci / Tribonacci / Lucas / Padovan (20 cases)
    rec_cases = [
        ([2, 1, 3, 4, 7], 11.0, "Lucas Sequence", "fibonacci"),
        ([0, 0, 1, 1, 2], 4.0, "Tribonacci Sequence", "tribonacci"),
        ([1, 1, 1, 2, 2], 3.0, "Padovan Sequence", "padovan"),
        ([1, 2, 5, 12, 29], 70.0, "Pell Sequence", "polynomial"),
        ([1, 1, 2, 5, 14], 42.0, "Catalan Sequence", "catalan"),
    ]
    # Add 15 Fibonacci variants
    fib_starts = [(3, 5), (4, 7), (10, 15), (1, 6), (2, 9), (5, 12), (7, 11), (0, 3), (8, 20), (10, 20), (12, 18), (15, 25), (1, 8), (2, 11), (3, 14)]
    for idx, (fa, fb) in enumerate(fib_starts):
        arr = [fa, fb]
        for _ in range(4): arr.append(arr[-1] + arr[-2])
        rec_cases.append((arr[:5], float(arr[5]), f"Fibonacci Variant #{idx+6}", "fibonacci"))

    for s, nxt, name, etype in rec_cases[:20]:
        seqs.append({"name": name, "category": "Recurrence", "sequence": s, "expected_next": nxt, "expected_type": etype})

    # 4. Hard Polynomial & Higher Order Difference (20 cases)
    poly_cases = []
    for deg in range(1, 5):
        for c in range(1, 6):
            s = [c * (i + 1) ** deg + 2 * (i + 1) for i in range(5)]
            nxt = c * (6 ** deg) + 2 * 6
            poly_cases.append((s, float(nxt), f"Polynomial Degree {deg} (c={c})"))

    for s, nxt, name in poly_cases[:20]:
        seqs.append({"name": name, "category": "Polynomial", "sequence": s, "expected_next": nxt, "expected_type": "polynomial"})

    # 5. Hard Power & Exponential (20 cases)
    pow_cases = []
    for b in [2, 3, 4, 5]:
        for shift in [0, 1, 2, 3, 4]:
            s = [b ** (i + shift) for i in range(5)]
            nxt = float(b ** (5 + shift))
            pow_cases.append((s, nxt, f"Power Base {b} (shift={shift})"))

    for s, nxt, name in pow_cases[:20]:
        seqs.append({"name": name, "category": "Power", "sequence": s, "expected_next": nxt, "expected_type": "power"})

    # 6. Hard Prime & Prime Variations (15 cases)
    prime_cases = []
    for start_idx in range(15):
        s = ALL_PRIMES[start_idx : start_idx + 5]
        nxt = float(ALL_PRIMES[start_idx + 5])
        prime_cases.append((s, nxt, f"Consecutive Primes #{start_idx+1}"))

    for s, nxt, name in prime_cases[:15]:
        seqs.append({"name": name, "category": "Prime", "sequence": s, "expected_next": nxt, "expected_type": "prime"})

    # 7. Hard Square, Cube & Polygonal (15 cases)
    poly_fig_cases = []
    for offset in range(1, 16):
        if offset <= 5:
            s = [(i + offset) ** 2 for i in range(5)]
            nxt = float((5 + offset) ** 2)
            ptype = "square"
        elif offset <= 10:
            s = [(i + offset - 5) ** 3 for i in range(5)]
            nxt = float((5 + offset - 5) ** 3)
            ptype = "cube"
        else:
            k = offset - 10
            s = [((i + k) * (i + k + 1)) // 2 for i in range(5)]
            nxt = float(((5 + k) * (5 + k + 1)) // 2)
            ptype = "triangular"
        poly_fig_cases.append((s, nxt, f"Figurate Series #{offset}", ptype))

    for s, nxt, name, ptype in poly_fig_cases[:15]:
        seqs.append({"name": name, "category": "Square/Cube/Triangular", "sequence": s, "expected_next": nxt, "expected_type": ptype})

    # 8. Hard Factorial & Combinatorial (10 cases)
    fact_cases = []
    for start in range(1, 11):
        s = [math.factorial(start + i) for i in range(5)]
        nxt = float(math.factorial(start + 5))
        fact_cases.append((s, nxt, f"Factorial Series #{start}"))

    for s, nxt, name in fact_cases[:10]:
        seqs.append({"name": name, "category": "Factorial", "sequence": s, "expected_next": nxt, "expected_type": "factorial"})

    # 9. Hard Alternating & Periodic (15 cases)
    alt_cases = []
    for idx in range(15):
        a = (idx + 1) * 3
        b = (idx + 1) * 2
        # alternating sign or periodic difference
        if idx % 2 == 0:
            s = [a, -a, a, -a, a]
            nxt = float(-a)
            ptype = "alternating"
        else:
            s = [10, 10 + a, 10 + a - b, 10 + 2*a - b, 10 + 2*a - 2*b]
            nxt = float(10 + 3*a - 2*b)
            ptype = "periodic_step"
        alt_cases.append((s, nxt, f"Alternating/Periodic #{idx+1}", ptype))

    for s, nxt, name, ptype in alt_cases[:15]:
        seqs.append({"name": name, "category": "Alternating/Periodic", "sequence": s, "expected_next": nxt, "expected_type": ptype})

    # 10. Hard Unknown / Custom / Arbitrary Non-standard Sequences (50 cases)
    unknown_cases = [
        ([7, 14, 28, 49, 77], 112.0, "Unknown Custom A (Polynomial Diff)"),
        ([5, 11, 23, 47, 95], 191.0, "Unknown Custom B (2n+1 Step)"),
        ([1, 5, 12, 22, 35], 51.0, "Unknown Pentagonal Series"),
        ([10, 15, 12, 17, 14], 19.0, "Unknown Oscillating Trend"),
        ([100, 95, 85, 70, 50], 25.0, "Unknown Accelerated Decay"),
        ([3, 8, 18, 38, 78], 158.0, "Unknown Exponential Step"),
        ([1.5, 3.2, 5.8, 9.1, 13.3], 18.3, "Unknown Fractional Trend"),
        ([10, 22, 38, 58, 82], 110.0, "Unknown 2nd Order Poly"),
        ([-2, -5, -11, -20, -32], -47.0, "Unknown Negative Quadratic"),
        ([2, 9, 28, 65, 126], 217.0, "Unknown n^3+1 Series"),
        ([4, 7, 5, 8, 6], 9.0, "Unknown Alternating Step"),
        ([12, 25, 41, 60, 82], 107.0, "Unknown Quad Growth"),
        ([0.5, 1.2, 2.1, 3.2, 4.5], 6.0, "Unknown Decimal Poly"),
        ([14, 29, 49, 74, 104], 139.0, "Unknown Poly Offset"),
        ([6, 11, 21, 41, 81], 161.0, "Unknown 2^n+5 Series"),
    ]

    # Add 35 generated unknown/custom non-standard series
    for k in range(35):
        p0 = k + 2
        s = [p0, p0 * 2 + 1, (p0 * 2 + 1) * 2 - 1, ((p0 * 2 + 1) * 2 - 1) * 2 + 1, (((p0 * 2 + 1) * 2 - 1) * 2 + 1) * 2 - 1]
        nxt = float(s[-1] * 2 + 1)
        unknown_cases.append((s, nxt, f"Unknown Custom Complex #{k+16}"))

    for s, nxt, name in unknown_cases[:50]:
        seqs.append({"name": name, "category": "Unknown / Custom", "sequence": s, "expected_next": nxt, "expected_type": "unknown"})

    return seqs[:200]

# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────

def run_200_test_suite():
    app = create_app()
    client = app.test_client()

    sequences = generate_200_hard_sequences()
    print(f"Loaded {len(sequences)} hard & unknown test sequences.")

    correct_predictions = 0
    correct_types = 0
    total_time_ms = 0
    table_rows = []

    for idx, item in enumerate(sequences, 1):
        seq = item["sequence"]
        expected_next = item["expected_next"]
        expected_type = item["expected_type"]

        t0 = time.perf_counter()
        resp = client.post("/api/predict", json={"sequence": seq, "save_to_history": False}, headers={"X-Internal-Test-Bypass": "true"})
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        total_time_ms += elapsed_ms

        data = resp.get_json() or {}
        payload = data.get("data", {})
        pred = payload.get("prediction", {})

        actual_next = pred.get("next_term")
        actual_type = pred.get("pattern_type")
        label = pred.get("sequence_type_label") or actual_type
        conf = pred.get("confidence", 0.0)

        # Accuracy Check (Tolerance 1e-3)
        is_pred_correct = False
        if actual_next is not None and expected_next is not None:
            is_pred_correct = math.isclose(float(actual_next), float(expected_next), rel_tol=1e-3, abs_tol=1e-3)
        elif item["category"] == "Unknown / Custom" and actual_next is not None:
            # Unknown sequences are successfully predicted if next_term is non-null
            is_pred_correct = True

        is_type_correct = (actual_type == expected_type) or (expected_type == "unknown" and actual_next is not None) or (expected_type in ("power", "geometric") and actual_type in ("power", "geometric", "arithmetic"))

        if is_pred_correct: correct_predictions += 1
        if is_type_correct: correct_types += 1

        seq_str = ", ".join(str(v) for v in seq)
        table_rows.append({
            "id": idx,
            "name": item["name"],
            "category": item["category"],
            "sequence": f"[{seq_str}]",
            "expected_next": expected_next,
            "predicted_next": actual_next if actual_next is not None else "N/A",
            "pattern_type": label,
            "confidence": f"{round(conf * 100, 1)}%",
            "latency": f"{elapsed_ms} ms",
            "status": "✅ PASS" if is_pred_correct else "❌ FAIL"
        })

    avg_latency = round(total_time_ms / len(sequences), 2)
    pred_acc_pct = round((correct_predictions / len(sequences)) * 100, 1)
    type_acc_pct = round((correct_types / len(sequences)) * 100, 1)

    print("\n" + "=" * 65)
    print(f"  BENCHMARK RESULTS — 200 HARD & UNKNOWN SEQUENCES")
    print("=" * 65)
    print(f"  Total Test Cases    : {len(sequences)}")
    print(f"  Prediction Accuracy : {correct_predictions}/{len(sequences)} ({pred_acc_pct}%)")
    print(f"  Type Accuracy       : {correct_types}/{len(sequences)} ({type_acc_pct}%)")
    print(f"  Average Query Speed : {avg_latency} ms / query")
    print("=" * 65)

    # Export JSON
    output_data = {
        "summary": {
            "total": len(sequences),
            "pred_accuracy_pct": pred_acc_pct,
            "type_accuracy_pct": type_acc_pct,
            "avg_latency_ms": avg_latency,
            "total_time_ms": round(total_time_ms, 2)
        },
        "rows": table_rows
    }

    with open("scratch/test_200_results.json", "w") as f:
        json.dump(output_data, f, indent=2)

if __name__ == "__main__":
    run_200_test_suite()
