
import os
import requests
import pandas as pd
import zipfile
import io
import sys

def download_file(url, target_path):
    print(f"Downloading from {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded to {target_path}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def get_phishtank_data(limit=10000):
    url = "http://data.phishtank.com/data/online-valid.csv"
    local_path = "data/phishtank.csv"
    
    # Try to download if not exists or force download logic could be added
    if not os.path.exists(local_path):
        print("PhishTank data not found locally.")
        # Note: PhishTank sometimes blocks automated requests without API key or User-Agent
        headers = {'User-Agent': 'PhishingURLDetector/1.0'}
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=15)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Downloaded PhishTank data.")
        except Exception as e:
            print(f"Error downloading PhishTank data: {e}")
            print("Please download manually from http://data.phishtank.com/data/online-valid.csv and place in data/phishtank.csv if this persists.")
            return None

    try:
        df = pd.read_csv(local_path)
        print(f"Loaded {len(df)} phishing URLs from PhishTank.")
        # Filter for valid entries if needed, extract URL
        if 'url' in df.columns:
            return df['url'].sample(n=min(len(df), limit), random_state=42).tolist()
        else:
            print("PhishTank CSV missing 'url' column.")
            return None
    except Exception as e:
        print(f"Error reading PhishTank data: {e}")
        return None

def get_legitimate_data(limit=10000):
    # Setup sources: Primary (Tranco), Secondary (Majestic/Other)
    sources = [
        {
            "name": "Tranco",
            "url": "https://tranco-list.eu/top-1m.csv.zip",
            "type": "zip",
            "filename_in_zip": "top-1m.csv" 
        },
        {
            "name": "Majestic Million (Fallback)",
            "url": "https://downloads.majestic.com/majestic_million.csv",
            "type": "csv"
        }
    ]
    
    for source in sources:
        print(f"Attempting to fetch legitimate domains from {source['name']}...")
        try:
            headers = {'User-Agent': 'PhishingURLDetector/1.0'}
            response = requests.get(source['url'], headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            df = None
            if source['type'] == 'zip':
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    # Find the CSV in the zip
                    target_file = source.get('filename_in_zip')
                    if not target_file:
                        target_file = z.namelist()[0]
                        
                    with z.open(target_file) as f:
                        df = pd.read_csv(f, header=None)
            else:
                # Direct CSV
                df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
            
            # Standardization: We expect a 'domain' column or the domain to be the 2nd column
            print(f"Loaded raw data with shape: {df.shape}")
            
            # Tranco/Majestic usually: Rank, Domain
            # Let's inspect columns to find the domain column
            domain_col = None
            if len(df.columns) >= 2:
                 # Assume 2nd column is domain if unnamed
                 domain_col = df.columns[1]
            elif 'Domain' in df.columns:
                 domain_col = 'Domain'
            elif 'domain' in df.columns:
                 domain_col = 'domain'
            else:
                # Fallback to 1st column if only 1 exists
                domain_col = df.columns[0]
                
            print(f"Using column '{domain_col}' for domains.")
            
            domains = df[domain_col].astype(str).sample(n=min(len(df), limit), random_state=42)
            urls = ["https://www." + d for d in domains]
            print(f"Successfully loaded {len(urls)} legitimate URLs from {source['name']}.")
            return urls
            
        except Exception as e:
            print(f"Failed to load from {source['name']}: {e}")
            continue
            
    print("All legitimate data sources failed.")
    return None

def main():
    if not os.path.exists('data'):
        os.makedirs('data')

    limit = 5000 # Default limit per class
    
    # Check args for limit
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass
            
    print(f"Targeting {limit} samples per class...")
    
    phishing_urls = get_phishtank_data(limit)
    legitimate_urls = get_legitimate_data(limit)
    
    if not phishing_urls or not legitimate_urls:
        print("Failed to acquire one or both datasets.")
        return

    # Create balanced dataset
    data = []
    
    for url in phishing_urls:
        data.append({'URL': url, 'Label': 'Phishing'})
        
    for url in legitimate_urls:
        data.append({'URL': url, 'Label': 'Legitimate'})
        
    df = pd.DataFrame(data)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    output_path = 'data/training_dataset.csv'
    df.to_csv(output_path, index=False)
    print(f"Success! Saved {len(df)} URLs to {output_path}")
    print(f"Phishing: {len(phishing_urls)}")
    print(f"Legitimate: {len(legitimate_urls)}")

if __name__ == "__main__":
    main()
