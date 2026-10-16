import requests
import json

def print_keys():
    url = "https://oeis.org/search?q=1,1,2,3,5,8&fmt=json"
    r = requests.get(url, timeout=5)
    data = r.json()
    if data:
        first = data[0]
        print("Keys:", list(first.keys()))
        print("number:", first.get("number"))
        print("id:", first.get("id"))
        # Print a list of standard fields
        for k in ['number', 'id', 'name', 'comment', 'formula']:
            print(f"{k}: {first.get(k)}")
    else:
        print("No data")

if __name__ == "__main__":
    print_keys()
