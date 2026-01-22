import requests
import zipfile
import io
import os
import sys

def download_and_inspect():
    url = "https://www.kaggle.com/api/v1/datasets/download/shashwatwork/phishing-dataset-for-machine-learning"
    target_zip = "data/kaggle_dataset.zip"
    extract_dir = "data/kaggle_dataset"
    
    if not os.path.exists("data"):
        os.makedirs("data")
        
    print(f"Downloading from {url}...")
    try:
        # Follow redirects is crucial for Kaggle
        response = requests.get(url, stream=True, allow_redirects=True)
        
        # Check if we got a login page or error (Kaggle often redirects to login)
        if "login" in response.url or response.status_code != 200:
            print(f"Warning: URL redirected to {response.url} or status {response.status_code}")
            # We will try to download anyway in case it's a public link that works for some reason
            
        with open(target_zip, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        # Check size associated with potential failure
        if os.path.getsize(target_zip) < 2000:
            print("Downloaded file is very small (< 2KB), likely an HTML login page or error.")
            with open(target_zip, 'r', errors='ignore') as f:
                print("Content sample:", f.read(500))
            return

        print(f"Downloaded {os.path.getsize(target_zip)} bytes.")
        
        print("Extracting...")
        with zipfile.ZipFile(target_zip, 'r') as z:
            z.extractall(extract_dir)
            print(f"Extracted to {extract_dir}:")
            for name in z.namelist():
                print(f" - {name}")
                if name.endswith('.csv'):
                    dataset_path = os.path.join(extract_dir, name)
                    print(f"\ndataset located at: {dataset_path}")
                    with open(dataset_path, 'r', encoding='utf-8', errors='replace') as f:
                        print("\nFirst 5 lines:")
                        for _ in range(5):
                            print(f.readline().strip())

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_and_inspect()
