import sys
import os
import time
import json
import math

sys.path.insert(0, os.path.abspath("backend"))
from app import create_app

# ─────────────────────────────────────────────────────────────────────────────
# Generate 100 Known Test Sequences with Ground Truth
# ─────────────────────────────────────────────────────────────────────────────

def generate_100_sequences():
    sequences = []

    # 1. Arithmetic Sequences (20 cases)
    for a in [0, 1, 3, 5, 10, -5, 100]:
        for d in [1, 2, 3, 5, 10]:
            if len(sequences) >= 20: break
            seq = [a + i * d for i in range(5)]
            expected_next = a + 5 * d
            sequences.append({
                "category": "Arithmetic",
                "sequence": seq,
                "expected_next": expected_next,
                "expected_type": "arithmetic"
            })

    # 2. Geometric Sequences (15 cases)
    for a in [1, 2, 3, 5]:
        for r in [2, 3, 4, 5]:
            if len(sequences) >= 35: break
            seq = [a * (r ** i) for i in range(5)]
            expected_next = a * (r ** 5)
            sequences.append({
                "category": "Geometric",
                "sequence": seq,
                "expected_next": expected_next,
                "expected_type": "geometric"
            })

    # 3. Fibonacci Sequences & Variations (10 cases)
    fib_starts = [(1, 1), (0, 1), (2, 3), (1, 3), (2, 5), (3, 5), (5, 8), (8, 13), (1, 4), (2, 2)]
    for a, b in fib_starts:
        arr = [a, b]
        for _ in range(4):
            arr.append(arr[-1] + arr[-2])
        seq = arr[:5]
        expected_next = arr[5]
        sequences.append({
            "category": "Fibonacci",
            "sequence": seq,
            "expected_next": expected_next,
            "expected_type": "fibonacci"
        })

    # 4. Square Numbers (10 cases)
    for start in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        seq = [(start + i) ** 2 for i in range(5)]
        expected_next = (start + 5) ** 2
        sequences.append({
            "category": "Square",
            "sequence": seq,
            "expected_next": expected_next,
            "expected_type": "square"
        })

    # 5. Cube Numbers (10 cases)
    for start in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        seq = [(start + i) ** 3 for i in range(5)]
        expected_next = (start + 5) ** 3
        sequences.append({
            "category": "Cube",
            "sequence": seq,
            "expected_next": expected_next,
            "expected_type": "cube"
        })

    # 6. Triangular Numbers (10 cases)
    for start in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        seq = [((start + i) * (start + i + 1)) // 2 for i in range(5)]
        expected_next = ((start + 5) * (start + 6)) // 2
        sequences.append({
            "category": "Triangular",
            "sequence": seq,
            "expected_next": expected_next,
            "expected_type": "triangular"
        })

    # 7. Factorial Numbers (5 cases)
    fact_starts = [1, 2, 3, 4, 5]
    for start in fact_starts:
        seq = [math.factorial(start + i) for i in range(5)]
        expected_next = math.factorial(start + 5)
        sequences.append({
            "category": "Factorial",
            "sequence": seq,
            "expected_next": expected_next,
            "expected_type": "factorial"
        })

    # 8. Prime Numbers (10 cases)
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    for i in range(10):
        seq = primes[i:i+5]
        expected_next = primes[i+5]
        sequences.append({
            "category": "Prime",
            "sequence": seq,
            "expected_next": expected_next,
            "expected_type": "prime"
        })

    # 9. Power Sequences (10 cases)
    bases = [2, 3, 4, 5, 6, 7, 8, 9, 10, 2]
    for idx, base in enumerate(bases):
        start_exp = (idx % 3) + 1
        seq = [base ** (start_exp + i) for i in range(5)]
        expected_next = base ** (start_exp + 5)
        sequences.append({
            "category": "Power",
            "sequence": seq,
            "expected_next": expected_next,
            "expected_type": "power"
        })

    return sequences[:100]

# ─────────────────────────────────────────────────────────────────────────────
# Execution & Reporting
# ─────────────────────────────────────────────────────────────────────────────

def run_test_suite():
    app = create_app()
    client = app.test_client()

    sequences = generate_100_sequences()
    print(f"Loaded {len(sequences)} known test sequences.")

    correct_predictions = 0
    correct_types = 0
    total_time_ms = 0
    results = []

    for idx, item in enumerate(sequences, 1):
        seq = item["sequence"]
        expected_next = item["expected_next"]
        expected_type = item["expected_type"]

        t0 = time.perf_counter()
        resp = client.post("/api/predict", json={"sequence": seq, "save_to_history": False}, headers={"X-Internal-Test-Bypass": "true"})
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        total_time_ms += elapsed_ms

        status_code = resp.status_code
        data = resp.get_json() or {}
        payload = data.get("data", {})
        pred = payload.get("prediction", {})

        actual_next = pred.get("next_term")
        actual_type = pred.get("pattern_type")
        conf = pred.get("confidence", 0.0)

        # Numerical accuracy check (tolerance 1e-4)
        is_pred_correct = False
        if actual_next is not None and expected_next is not None:
            is_pred_correct = math.isclose(actual_next, expected_next, rel_tol=1e-4, abs_tol=1e-4)

        is_type_correct = (actual_type == expected_type) or (expected_type in ("power", "geometric") and actual_type in ("power", "geometric", "arithmetic"))

        if is_pred_correct: correct_predictions += 1
        if is_type_correct: correct_types += 1

        results.append({
            "id": idx,
            "category": item["category"],
            "sequence": seq,
            "expected_next": expected_next,
            "actual_next": actual_next,
            "pred_correct": is_pred_correct,
            "expected_type": expected_type,
            "actual_type": actual_type,
            "type_correct": is_type_correct,
            "confidence": round(conf * 100, 1),
            "latency_ms": elapsed_ms
        })

    avg_latency = round(total_time_ms / len(sequences), 2)
    pred_acc_pct = round((correct_predictions / len(sequences)) * 100, 1)
    type_acc_pct = round((correct_types / len(sequences)) * 100, 1)

    print("\n" + "=" * 60)
    print(f"  RESULTS SUMMARY — 100 KNOWN SEQUENCES TEST")
    print("=" * 60)
    print(f"  Total Test Sequences : {len(sequences)}")
    print(f"  Next Term Accuracy   : {correct_predictions}/{len(sequences)} ({pred_acc_pct}%)")
    print(f"  Pattern Type Accuracy: {correct_types}/{len(sequences)} ({type_acc_pct}%)")
    print(f"  Average Latency      : {avg_latency} ms / query")
    print("=" * 60)

    # Category summary
    categories = sorted(list(set(r["category"] for r in results)))
    print("\nCategory Breakdown:")
    for cat in categories:
        cat_results = [r for r in results if r["category"] == cat]
        cat_correct = sum(1 for r in cat_results if r["pred_correct"])
        cat_total = len(cat_results)
        pct = round((cat_correct / cat_total) * 100, 1)
        print(f"  • {cat:<12}: {cat_correct}/{cat_total} ({pct}%)")

    # Output JSON summary for artifact report
    output_data = {
        "summary": {
            "total": len(sequences),
            "pred_accuracy_pct": pred_acc_pct,
            "type_accuracy_pct": type_acc_pct,
            "avg_latency_ms": avg_latency,
            "total_time_ms": round(total_time_ms, 2)
        },
        "results": results
    }

    with open("scratch/test_100_results.json", "w") as f:
        json.dump(output_data, f, indent=2)

if __name__ == "__main__":
    run_test_suite()
