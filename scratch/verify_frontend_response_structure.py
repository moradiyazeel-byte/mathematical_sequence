import sys
import os
import json

sys.path.insert(0, os.path.abspath("backend"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from app import create_app

def test_structure():
    app = create_app()
    client = app.test_client()

    print("--- 1. Testing Known Sequence [1, 3, 5, 7, 9] ---")
    res1 = client.post("/api/predict", json={"sequence": [1, 3, 5, 7, 9]})
    data1 = res1.get_json()["data"]
    print(f"Pattern Label : {data1['prediction']['sequence_type_label']}")
    print(f"Next Term     : {data1['prediction']['next_term']}")
    print(f"Formula       : {data1['explanation']['formula']}")

    print("\n--- 2. Testing Unknown Sequence [7, 14, 28, 49, 77] ---")
    res2 = client.post("/api/predict", json={"sequence": [7, 14, 28, 49, 77]})
    data2 = res2.get_json()["data"]
    print(f"Pattern Label : {data2['prediction']['sequence_type_label']}")
    print(f"Next Term     : {data2['prediction']['next_term']}")
    print(f"Formula       : {data2['explanation']['formula']}")

if __name__ == "__main__":
    test_structure()
