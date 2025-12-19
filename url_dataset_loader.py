"""
URL Dataset Loader
Loads seed URLs from CSV for training and testing
"""

import pandas as pd
import os
from pathlib import Path


class URLDatasetLoader:
    """Load and manage URL datasets"""
    
    def __init__(self, csv_path: str = 'data/seed_urls.csv'):
        self.csv_path = csv_path
        self.data = None
        self.phishing_urls = []
        self.legitimate_urls = []
        
    def load_dataset(self) -> bool:
        """Load CSV dataset"""
        try:
            if not os.path.exists(self.csv_path):
                print(f"[ERROR] CSV file not found: {self.csv_path}")
                return False
            
            self.data = pd.read_csv(self.csv_path)
            print(f"[OK] Loaded dataset: {len(self.data)} URLs")
            
            # Separate URLs by label
            self.phishing_urls = self.data[self.data['Label'] == 'Phishing']['URL'].tolist()
            self.legitimate_urls = self.data[self.data['Label'] == 'Legitimate']['URL'].tolist()
            
            print(f"[OK] Phishing URLs: {len(self.phishing_urls)}")
            print(f"[OK] Legitimate URLs: {len(self.legitimate_urls)}")
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load dataset: {str(e)}")
            return False
    
    def get_phishing_urls(self):
        """Get all phishing URLs"""
        return self.phishing_urls
    
    def get_legitimate_urls(self):
        """Get all legitimate URLs"""
        return self.legitimate_urls
    
    def get_all_urls(self):
        """Get all URLs with labels"""
        if self.data is None:
            return []
        return self.data.to_dict('records')
    
    def get_dataset_info(self) -> dict:
        """Get dataset information"""
        return {
            'total_urls': len(self.data) if self.data is not None else 0,
            'phishing_count': len(self.phishing_urls),
            'legitimate_count': len(self.legitimate_urls),
            'file_path': self.csv_path,
            'loaded': self.data is not None
        }
    
    def validate_urls(self) -> dict:
        """Validate URLs in dataset"""
        validation = {
            'total': len(self.data) if self.data is not None else 0,
            'valid': 0,
            'invalid': 0,
            'issues': []
        }
        
        if self.data is None:
            return validation
        
        for idx, row in self.data.iterrows():
            url = row['URL']
            label = row['Label']
            
            # Check URL format
            if not url.startswith(('http://', 'https://')):
                validation['invalid'] += 1
                validation['issues'].append(f"Row {idx}: Invalid URL format - {url}")
            elif label not in ['Phishing', 'Legitimate']:
                validation['invalid'] += 1
                validation['issues'].append(f"Row {idx}: Invalid label - {label}")
            else:
                validation['valid'] += 1
        
        return validation


# Quick test when run as script
if __name__ == '__main__':
    print("\n[URL DATASET LOADER TEST]")
    print("="*70)
    
    loader = URLDatasetLoader('data/seed_urls.csv')
    
    if loader.load_dataset():
        info = loader.get_dataset_info()
        print("\nDataset Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        print("\nValidation Results:")
        validation = loader.validate_urls()
        for key, value in validation.items():
            if key != 'issues':
                print(f"  {key}: {value}")
        
        if validation['issues']:
            print("\nIssues found:")
            for issue in validation['issues'][:5]:  # Show first 5
                print(f"  - {issue}")
        
        print("\nSample URLs:")
        print("\nPhishing samples:")
        for url in loader.get_phishing_urls()[:3]:
            print(f"  - {url}")
        
        print("\nLegitimate samples:")
        for url in loader.get_legitimate_urls()[:3]:
            print(f"  - {url}")
    
    print("\n" + "="*70)
