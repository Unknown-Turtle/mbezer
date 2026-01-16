import requests
import sys

try:
    url = "http://127.0.0.1:8001/upload?method=pca"
    files = {'file': open('test_data.csv', 'rb')}
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        print("Response JSON keys:", data.keys())
        if "points" in data and len(data["points"]) > 0:
            print("Success: 'points' found in response.")
            print("First point sample:", data["points"][0])
        else:
            print("Failure: 'points' missing or empty.")
            sys.exit(1)
    else:
        print(f"Failure: Status code {response.status_code}")
        print(response.text)
        sys.exit(1)

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
