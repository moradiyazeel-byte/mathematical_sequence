import sys
import os
import json
import math

sys.path.insert(0, os.path.abspath("backend"))
from app import create_app

def run_unknown_tests():
    app = create_app()
    client = app.test_client()

    unknown_sequences = [
        {"name": "Arbitrary Custom Sequence A", "seq": [7, 14, 28, 49, 77]},
        {"name": "Complex Mixed Step Sequence", "seq": [5, 11, 23, 47, 95]},
        {"name": "Polygonal 2nd Order Sequence", "seq": [1, 5, 12, 22, 35]},
        {"name": "Oscillating Trend Sequence", "seq": [10, 15, 12, 17, 14, 19]},
        {"name": "Non-linear Decay Sequence", "seq": [100, 95, 85, 70, 50]},
        {"name": "Custom Growth Sequence", "seq": [3, 8, 18, 38, 78]},
        {"name": "Fractional Slope Sequence", "seq": [1.5, 3.2, 5.8, 9.1, 13.3]},
        {"name": "Random-looking Step Series", "seq": [10, 22, 38, 58, 82]},
        {"name": "Negative Slope Custom Series", "seq": [-2, -5, -11, -20, -32]},
        {"name": "Large Value Trend Sequence", "seq": [1000, 1500, 2250, 3375, 5062.5]},
        {"name": "Polynomial Order 3 Series", "seq": [2, 9, 28, 65, 126]},
        {"name": "Alternating Difference Series", "seq": [4, 7, 5, 8, 6, 9]},
        {"name": "Custom Step Series", "seq": [12, 25, 41, 60, 82]},
        {"name": "Arbitrary Real Values", "seq": [0.5, 1.2, 2.1, 3.2, 4.5]},
        {"name": "Non-standard Integer Series", "seq": [14, 29, 49, 74, 104]},
    ]

    print("=" * 65)
    print("  TESTING UNKNOWN & CUSTOM SEQUENCES PREDICTION ENGINE")
    print("=" * 65)

    results = []
    for item in unknown_sequences:
        seq = item["seq"]
        res = client.post("/api/predict", json={"sequence": seq, "save_to_history": False})
        assert res.status_code == 200

        data = res.get_json() or {}
        payload = data.get("data", {})
        pred = payload.get("prediction", {})
        expl = payload.get("explanation", {})

        actual_next = pred.get("next_term")
        pattern_type = pred.get("pattern_type")
        label = pred.get("sequence_type_label")
        conf = pred.get("confidence", 0.0)

        print(f"\nSequence: {seq}")
        print(f"  • Name            : {item['name']}")
        print(f"  • Predicted Next  : {actual_next}")
        print(f"  • Detected Pattern: {label} ({pattern_type})")
        print(f"  • Confidence      : {round(conf * 100, 1)}%")
        print(f"  • Explanation     : {expl.get('summary')}")

        assert actual_next is not None, f"Failed: {item['name']} returned None prediction!"

        results.append({
            "name": item["name"],
            "sequence": seq,
            "predicted_next": actual_next,
            "pattern_type": pattern_type,
            "label": label,
            "confidence": round(conf * 100, 1)
        })

    print("\n" + "=" * 65)
    print(f"  SUCCESS: All {len(unknown_sequences)} unknown sequences successfully predicted!")
    print("=" * 65)

if __name__ == "__main__":
    run_unknown_tests()
