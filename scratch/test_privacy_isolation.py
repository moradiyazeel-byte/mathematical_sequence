import requests
import uuid

API_BASE = "http://127.0.0.1:5000/api"

def run_privacy_tests():
    print("=== STARTING PRIVACY & HISTORY ISOLATION TESTS (LOGGED-IN ONLY DB) ===")
    
    # 1. Register and login User A
    username_a = f"usera_{uuid.uuid4().hex[:6]}"
    email_a = f"{username_a}@example.com"
    password = "password123"
    
    print(f"Registering User A ({username_a})...")
    r = requests.post(f"{API_BASE}/auth/register", json={
        "username": username_a, "email": email_a, "password": password, "full_name": "User A"
    })
    assert r.status_code == 201
    
    r = requests.post(f"{API_BASE}/auth/login", json={"username": username_a, "password": password})
    assert r.status_code == 200
    token_a = r.json()["data"]["token"]
    headers_a = {"Authorization": f"Bearer {token_a}", "X-Internal-Test-Bypass": "true"}

    # 2. Register and login User B
    username_b = f"userb_{uuid.uuid4().hex[:6]}"
    email_b = f"{username_b}@example.com"
    
    print(f"Registering User B ({username_b})...")
    r = requests.post(f"{API_BASE}/auth/register", json={
        "username": username_b, "email": email_b, "password": password, "full_name": "User B"
    })
    assert r.status_code == 201
    
    r = requests.post(f"{API_BASE}/auth/login", json={"username": username_b, "password": password})
    assert r.status_code == 200
    token_b = r.json()["data"]["token"]
    headers_b = {"Authorization": f"Bearer {token_b}", "X-Internal-Test-Bypass": "true"}

    # 3. User A makes a prediction (Should persist in DB)
    print("User A making a prediction...")
    r = requests.post(f"{API_BASE}/predict", json={"sequence": [10, 20, 30, 40]}, headers=headers_a)
    assert r.status_code == 200
    pred_a_id = r.json()["data"]["id"]
    print(f"User A prediction ID: {pred_a_id}")
    assert pred_a_id is not None, "Expected database ID for User A prediction"

    # 4. User B makes a prediction (Should persist in DB)
    print("User B making a prediction...")
    r = requests.post(f"{API_BASE}/predict", json={"sequence": [5, 10, 15, 20]}, headers=headers_b)
    assert r.status_code == 200
    pred_b_id = r.json()["data"]["id"]
    print(f"User B prediction ID: {pred_b_id}")
    assert pred_b_id is not None, "Expected database ID for User B prediction"

    # 5. Guest makes a prediction (Should NOT persist in DB, returning ID as None or timestamp)
    print("Guest making a prediction...")
    r = requests.post(f"{API_BASE}/predict", json={"sequence": [100, 200, 300, 400]}, headers={"X-Internal-Test-Bypass": "true"})
    assert r.status_code == 200
    pred_guest_id = r.json()["data"]["id"]
    print(f"Guest prediction ID returned: {pred_guest_id}")
    assert pred_guest_id is None, "Expected guest prediction ID to be None (not saved in database)"

    # 6. Verify User A's history contains ONLY User A's prediction
    print("Checking User A's history...")
    r = requests.get(f"{API_BASE}/history", headers=headers_a)
    assert r.status_code == 200
    records_a = r.json()["data"]["records"]
    ids_a = [rec["id"] for rec in records_a]
    print(f"User A history records: {ids_a}")
    assert pred_a_id in ids_a, "User A history must contain User A's prediction"
    assert pred_b_id not in ids_a, "User A history must NOT contain User B's prediction"

    # 7. Verify User B's history contains ONLY User B's prediction
    print("Checking User B's history...")
    r = requests.get(f"{API_BASE}/history", headers=headers_b)
    assert r.status_code == 200
    records_b = r.json()["data"]["records"]
    ids_b = [rec["id"] for rec in records_b]
    print(f"User B history records: {ids_b}")
    assert pred_b_id in ids_b, "User B history must contain User B's prediction"
    assert pred_a_id not in ids_b, "User B history must NOT contain User A's prediction"

    # 8. Verify Guest's history is EMPTY in the backend database
    print("Checking Guest's history...")
    r = requests.get(f"{API_BASE}/history")
    assert r.status_code == 200
    records_guest = r.json()["data"]["records"]
    print(f"Guest history records in database: {records_guest}")
    assert len(records_guest) == 0, "Guest history in backend database must be empty"

    # 9. Verify cross-user detail access is forbidden (User B accessing User A's prediction)
    print("User B attempting to access User A's prediction details...")
    r = requests.get(f"{API_BASE}/predict/{pred_a_id}", headers=headers_b)
    print(f"Status code: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 403, "Expected 403 Forbidden for cross-user prediction access"

    # 10. Verify guest detail access is forbidden for registered predictions (Guest accessing User A's prediction)
    print("Guest attempting to access User A's prediction details...")
    r = requests.get(f"{API_BASE}/predict/{pred_a_id}")
    print(f"Status code: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 403, "Expected 403 Forbidden for guest access to registered user's prediction"

    # 11. Verify cross-user feedback submission is forbidden
    print("User B attempting to submit feedback on User A's prediction...")
    r = requests.post(f"{API_BASE}/predict/{pred_a_id}/feedback", json={"is_correct": True}, headers=headers_b)
    print(f"Status code: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 403, "Expected 403 Forbidden for cross-user feedback submission"

    # 12. Verify guest feedback on registered prediction is forbidden
    print("Guest attempting to submit feedback on User A's prediction...")
    r = requests.post(f"{API_BASE}/predict/{pred_a_id}/feedback", json={"is_correct": True})
    print(f"Status code: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 403, "Expected 403 Forbidden for guest feedback on user's prediction"

    # 13. Verify delete cross-user prediction is forbidden
    print("User B attempting to delete User A's prediction...")
    r = requests.delete(f"{API_BASE}/history/{pred_a_id}", headers=headers_b)
    print(f"Status code: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 404, "Expected 404 for cross-user delete"

    # 14. Verify delete guest prediction as guest returns 401
    print("Guest attempting to delete prediction...")
    r = requests.delete(f"{API_BASE}/history/{pred_a_id}")
    print(f"Status code: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 401, "Expected 401 Unauthorized for guest deletion"

    # 15. Verify clearing history as guest returns 401
    print("Guest clearing history...")
    r = requests.delete(f"{API_BASE}/history")
    print(f"Status code: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 401, "Expected 401 Unauthorized for guest clear history"

    # User A clearing their history should succeed
    print("User A clearing their history...")
    r = requests.delete(f"{API_BASE}/history", headers=headers_a)
    assert r.status_code == 200

    # User A history should be empty now
    r = requests.get(f"{API_BASE}/history", headers=headers_a)
    assert len(r.json()["data"]["records"]) == 0, "User A history should be cleared"

    # User B history should still be intact
    r = requests.get(f"{API_BASE}/history", headers=headers_b)
    assert pred_b_id in [rec["id"] for rec in r.json()["data"]["records"]], "User B history must remain intact"

    print("=== ALL PRIVACY AND HISTORY ISOLATION TESTS PASSED! ===")

if __name__ == "__main__":
    run_privacy_tests()
