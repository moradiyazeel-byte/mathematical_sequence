import requests

def test_oeis():
    seq = "1,1,2,3,5,8"
    url = f"https://oeis.org/search?q={seq}&fmt=json"
    print(f"Querying: {url}")
    try:
        r = requests.get(url, timeout=5)
        print(f"Status: {r.status_code}")
        data = r.json()
        print("Data Type:", type(data))
        print("Data content sample:")
        import pprint
        pprint.pprint(data[:2] if isinstance(data, list) else list(data.items())[:3])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_oeis()
