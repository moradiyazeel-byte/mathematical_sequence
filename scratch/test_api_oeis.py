import requests

def test_local_oeis():
    url = "http://localhost:5000/api/predict/oeis?sequence=1,1,2,3,5,8"
    print(f"Querying local backend: {url}")
    try:
        r = requests.get(url, timeout=5)
        print("Status Code:", r.status_code)
        data = r.json()
        print("Response JSON:")
        import pprint
        pprint.pprint(data)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_local_oeis()
