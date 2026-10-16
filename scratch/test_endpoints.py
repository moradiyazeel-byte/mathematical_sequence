import requests
import uuid

API_BASE = "http://localhost:5000/api"

def run_tests():
    print("=== Testing Registration, Login, and Authenticated Routes ===")
    
    # 1. Register a new random user
    username = f"testuser_{uuid.uuid4().hex[:6]}"
    email = f"{username}@example.com"
    password = "testpassword123"
    full_name = "Test User"
    
    print(f"Registering username: {username}...")
    reg_url = f"{API_BASE}/auth/register"
    reg_payload = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": full_name
    }
    
    r_reg = requests.post(reg_url, json=reg_payload)
    print(f"Registration status: {r_reg.status_code}")
    print(f"Registration response: {r_reg.json()}")
    assert r_reg.status_code == 201, "Expected registration status 201"
    
    # 2. Login as the new user
    print(f"Logging in as {username}...")
    login_url = f"{API_BASE}/auth/login"
    login_payload = {
        "username": username,
        "password": password
    }
    
    r_login = requests.post(login_url, json=login_payload)
    print(f"Login status: {r_login.status_code}")
    login_data = r_login.json()
    print(f"Login response: {login_data}")
    assert r_login.status_code == 200, "Expected login status 200"
    
    token = login_data["data"]["token"]
    print("Successfully retrieved JWT token.")
    
    # 3. Predict sequence with Token (Authenticated)
    print("Testing authenticated prediction...")
    pred_url = f"{API_BASE}/predict"
    pred_payload = {
        "sequence": [3, 6, 9, 12, 15]
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r_pred = requests.post(pred_url, json=pred_payload, headers=headers)
    print(f"Predict status: {r_pred.status_code}")
    pred_data = r_pred.json()
    print(f"Prediction result next term: {pred_data['data']['prediction']['next_term']}")
    assert r_pred.status_code == 200, "Expected predict status 200"
    assert pred_data["data"]["prediction"]["next_term"] == 18.0, "Expected next term to be 18"
    
    # 4. Fetch Profile with Token (Authenticated)
    print("Testing authenticated profile fetch...")
    profile_url = f"{API_BASE}/user/profile"
    r_profile = requests.get(profile_url, headers=headers)
    print(f"Profile status: {r_profile.status_code}")
    profile_data = r_profile.json()
    print(f"Profile response: {profile_data}")
    assert r_profile.status_code == 200, "Expected profile status 200"
    assert profile_data["data"]["username"] == username, "Expected matching username in profile"
    
    # 5. Fetch Profile without Token (Should fail with 401)
    print("Testing unauthenticated profile fetch (should fail)...")
    r_profile_guest = requests.get(profile_url)
    print(f"Profile guest status: {r_profile_guest.status_code}")
    print(f"Profile guest response: {r_profile_guest.json()}")
    assert r_profile_guest.status_code in (401, 403), "Expected 401 or 403 status for unauthorized profile access"
    
    print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
