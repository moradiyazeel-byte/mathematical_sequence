import json
import sys
import os
sys.path.insert(0, os.path.abspath("backend"))
from app import create_app

def run_tests():
    app = create_app()
    client = app.test_client()

    print("=== Testing 1. Health Endpoint ===")
    res = client.get("/api/health")
    print(res.status_code, res.get_json())
    assert res.status_code == 200

    print("\n=== Testing 2. Predict Endpoint ===")
    res = client.post("/api/predict", json={"sequence": [3, 7, 11, 15, 19]})
    print(res.status_code, json.dumps(res.get_json(), indent=2))
    assert res.status_code == 200

    print("\n=== Testing 3. Register Endpoint ===")
    reg_body = {
        "username": "testuser_api",
        "email": "testuser_api@example.com",
        "password": "Password123!",
        "full_name": "API Test User"
    }
    res = client.post("/api/auth/register", json=reg_body)
    print(res.status_code, res.get_json())

    print("\n=== Testing 4. Login Endpoint ===")
    res = client.post("/api/auth/login", json={"username": "testuser_api", "password": "Password123!"})
    print(res.status_code, res.get_json())
    data = res.get_json()
    token = data.get("data", {}).get("token")

    print("\n=== Testing 5. History Endpoint ===")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    res = client.get("/api/history", headers=headers)
    print(res.status_code, json.dumps(res.get_json(), indent=2))

if __name__ == "__main__":
    run_tests()
