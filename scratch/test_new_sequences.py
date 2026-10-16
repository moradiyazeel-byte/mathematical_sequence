import sys
import os

sys.path.insert(0, os.path.abspath("backend"))
from app import create_app

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        text = (text
                .replace('\u2212', '-')
                .replace('\u2022', '*')
                .replace('\u2705', '[PASS]')
                .replace('\u274c', '[FAIL]')
                .replace('\u2192', '->')
                .replace('\u2014', '--')
                .replace('\u00b7', '*')
                .replace('\u208a', '+')
                .replace('\u2081', '1')
                .replace('\u207f', '^n')
                .replace('\u207b', '-')
                .replace('\u00b9', '1')
                .replace('\u2215', '/')
                .replace('\u00b2', '^2')
                .replace('\u00b3', '^3')
                .replace('\u00d7', 'x')
               )
        try:
            print(text)
        except Exception:
            print(text.encode('ascii', errors='ignore').decode('ascii'))

def test_new_sequences():
    app = create_app()
    client = app.test_client()

    test_cases = [
        {
            "name": "Lucas Sequence",
            "seq": [2, 1, 3, 4, 7, 11],
            "expected_pattern": "lucas",
            "expected_next": 18.0
        },
        {
            "name": "Pell Sequence",
            "seq": [0, 1, 2, 5, 12, 29],
            "expected_pattern": "pell",
            "expected_next": 70.0
        },
        {
            "name": "Jacobsthal Sequence",
            "seq": [0, 1, 1, 3, 5, 11],
            "expected_pattern": "jacobsthal",
            "expected_next": 21.0
        },
        {
            "name": "Collatz Sequence (Even last term)",
            "seq": [10, 5, 16, 8, 4, 2],
            "expected_pattern": "collatz",
            "expected_next": 1.0
        },
        {
            "name": "Collatz Sequence (Odd last term)",
            "seq": [16, 8, 4, 2, 1],
            "expected_pattern": "collatz",
            "expected_next": 4.0
        },
        {
            "name": "Look-and-Say Sequence",
            "seq": [1, 11, 21, 1211, 111221],
            "expected_pattern": "look_and_say",
            "expected_next": 312211.0
        },
        {
            "name": "Pentagonal Sequence",
            "seq": [1, 5, 12, 22, 35],
            "expected_pattern": "pentagonal",
            "expected_next": 51.0
        },
        {
            "name": "Hexagonal Sequence",
            "seq": [1, 6, 15, 28, 45],
            "expected_pattern": "hexagonal",
            "expected_next": 66.0
        },
        {
            "name": "Oblong (Pronic) Sequence",
            "seq": [2, 6, 12, 20, 30],
            "expected_pattern": "oblong",
            "expected_next": 42.0
        },
        {
            "name": "Sum of Squares Sequence",
            "seq": [1, 5, 14, 30, 55],
            "expected_pattern": "sum_of_squares",
            "expected_next": 91.0
        },
        {
            "name": "Sum of Cubes Sequence",
            "seq": [1, 9, 36, 100],
            "expected_pattern": "sum_of_cubes",
            "expected_next": 225.0
        },
        {
            "name": "Mersenne Sequence",
            "seq": [1, 3, 7, 15, 31],
            "expected_pattern": "mersenne",
            "expected_next": 63.0
        }
    ]

    safe_print("=" * 70)
    safe_print("  RUNNING NEW SPECIAL SEQUENCES VERIFICATION TESTS")
    safe_print("=" * 70)

    all_passed = True
    for case in test_cases:
        safe_print(f"\nTesting: {case['name']}")
        safe_print(f"Sequence: {case['seq']}")

        res = client.post(
            "/api/predict",
            json={"sequence": case["seq"], "save_to_history": False},
            headers={"X-Internal-Test-Bypass": "true"}
        )

        if res.status_code != 200:
            safe_print(f"❌ FAIL: HTTP status {res.status_code}")
            safe_print(f"Response: {res.get_data(as_text=True)}")
            all_passed = False
            continue

        res_data = res.get_json() or {}
        payload = res_data.get("data", {})
        pred = payload.get("prediction", {})
        expl = payload.get("explanation", {})

        actual_pattern = pred.get("pattern_type")
        actual_next = pred.get("next_term")
        method = pred.get("method_used")
        conf = pred.get("confidence")
        formula = expl.get("formula")
        calc_text = expl.get("calculation")
        summary = expl.get("summary")

        safe_print(f"  • Pattern Detected : {actual_pattern} (Expected: {case['expected_pattern']})")
        safe_print(f"  • Next Term        : {actual_next} (Expected: {case['expected_next']})")
        safe_print(f"  • Method Used      : {method}")
        safe_print(f"  • Confidence       : {conf}")
        safe_print(f"  • Formula          : {formula}")
        safe_print(f"  • Calc Details     : {calc_text}")
        safe_print(f"  • Summary          : {summary}")

        # Assertions
        try:
            assert actual_pattern == case["expected_pattern"], f"Pattern mismatch! Got {actual_pattern}"
            assert abs(actual_next - case["expected_next"]) < 1e-4, f"Next term mismatch! Got {actual_next}"
            assert method == "rule", f"Expected rule engine to handle it, but got {method}"
            assert conf >= 0.95, f"Expected high confidence, but got {conf}"
            safe_print("✅ PASS")
        except AssertionError as e:
            safe_print(f"❌ FAIL: {e}")
            all_passed = False

    safe_print("\n" + "=" * 70)
    if all_passed:
        safe_print("  🎉 ALL NEW SPECIAL SEQUENCE TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        safe_print("  ❌ SOME TESTS FAILED. PLEASE CHECK LOGS.")
        sys.exit(1)

if __name__ == "__main__":
    test_new_sequences()
