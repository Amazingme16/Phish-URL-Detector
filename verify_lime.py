import requests
import time
import sys
import json

url = "http://127.0.0.1:5000/api/analyze"
payload = {"url": "http://paypa1.com/login"}

print(f"Testing URL: {payload['url']}")

try:
    # Try multiple times in case app is starting up
    for i in range(15):
        try:
            response = requests.post(url, json=payload)
            break
        except requests.exceptions.ConnectionError:
            print(f"Attempt {i+1}: Connection failed, retrying in 2s...")
            time.sleep(2)
    else:
        print("Failed to connect to app after 15 attempts.")
        sys.exit(1)

    if response.status_code == 200:
        data = response.json()
        print("Response received.")
        
        # Check for LIME analysis
        if 'lime_analysis' in data:
            print("[passwd] LIME Analysis found.")
            lime_data = data['lime_analysis']
            print(f"Local Prediction: {lime_data.get('local_prediction')}")
            
            features = lime_data.get('top_contributing_features', [])
            if features:
                print(f"Found {len(features)} contributing features.")
                print("Top 3:")
                for feature in features[:3]:
                    print(f" - {feature['feature']}: {feature['weight']}")
            else:
                print("[WARNING] No top contributing features found in LIME analysis.")
                
            if 'error' in lime_data:
                 print(f"[ERROR] LIME analysis returned error: {lime_data['error']}")
        else:
            print("[FAIL] LIME Analysis MISSING from response.")
            print("Keys found:", data.keys())
            
    else:
        print(f"Error: {response.status_code} - {response.text}")

except Exception as e:
    print(f"Test failed with exception: {e}")
