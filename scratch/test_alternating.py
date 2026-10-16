import sys
import os
import json

sys.path.insert(0, os.path.abspath("backend"))
from app import create_app

def test_alternating_cases():
    app = create_app()
    client = app.test_client()

    cases = [
        ([1, -1, 1, -1, 1], -1, "Alternating Sign Unit"),
        ([2, -4, 6, -8, 10], -12, "Alternating Sign Arithmetic"),
        ([1, 3, 1, 3, 1], 3, "Alternating Value (1, 3)"),
        ([4, 7, 4, 7, 4], 7, "Alternating Value (4, 7)"),
        ([10, 20, 10, 20, 10], 20, "Alternating Value (10, 20)"),
        ([1, 2, 3, 1, 2, 3], 1, "Periodic Cycle (1, 2, 3)"),
    ]

    print("=" * 65)
    print("  TESTING ALL ALTERNATING & PERIODIC SEQUENCES")
    print("=" * 65)

    for seq, expected, name in cases:
        res = client.post("/api/predict", json={"sequence": seq, "save_to_history": False})
        assert res.status_code == 200
        data = res.get_json()["data"]
        pred = data["prediction"]

        pattern = pred["pattern_type"]
        label = pred["sequence_type_label"]
        actual_next = pred["next_term"]
        conf = pred["confidence"]

        print(f"\n{name:<30} Sequence: {seq}")
        print(f"  • Expected Next : {expected}")
        print(f"  • Predicted Next: {actual_next}")
        print(f"  • Pattern Label : {label} ({pattern})")
        print(f"  • Confidence    : {round(conf * 100, 1)}%")

        assert actual_next == expected, f"Failed: Expected {expected}, got {actual_next}"

    print("\n" + "=" * 65)
    print("  ✅ ALL ALTERNATING SEQUENCES PASSED WITH 100% ACCURACY!")
    print("=" * 65)

if __name__ == "__main__":
    test_alternating_cases()
