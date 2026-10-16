import sys
import os
import json

sys.path.insert(0, os.path.abspath("backend"))
from app import create_app

def verify():
    app = create_app()
    client = app.test_client()

    unknown_test_cases = [
        [7, 14, 28, 49, 77],
        [5, 11, 23, 47, 95],
        [1, 4, 19, 3, 89],
        [100, 80, 55, 25, 0],
        [12, 19, 31, 50, 81],
    ]

    for seq in unknown_test_cases:
        res = client.post("/api/predict", json={"sequence": seq})
        assert res.status_code == 200
        data = res.get_json()["data"]
        pred = data["prediction"]
        print(f"Seq: {seq} -> Next: {pred['next_term']}, Label: {pred['sequence_type_label']}, Conf: {pred['confidence']}")
        assert pred['next_term'] is not None, "Next term should not be None!"

    print("\n✅ Verification Successful: All unknown sequences yield non-null predictions!")

if __name__ == "__main__":
    verify()
