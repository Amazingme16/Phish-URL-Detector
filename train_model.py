"""
Model Training Module
Trains Logistic Regression and Random Forest models for phishing detection
Supports loading seed URLs from CSV dataset and threat databases
"""

import pickle
import numpy as np
import sys
import json
import sqlite3
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from url_features import URLFeatureExtractor
from url_dataset_loader import URLDatasetLoader


def load_threat_database_json(json_path='threat_database_snapshot.json'):
    """Load phishing URLs from threat database JSON snapshot"""
    extractor = URLFeatureExtractor()
    X = []
    y = []
    
    if not os.path.exists(json_path):
        print(f"[WARNING] Threat database not found: {json_path}")
        return None, None
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        print(f"\nExtracting features from threat database JSON...")
        
        # Extract from active phishing links
        links_active = data.get('data', {}).get('links_active', [])
        for url in links_active:
            try:
                features = extractor.extract_features(url)
                X.append(features)
                y.append(1)  # All are phishing
            except Exception as e:
                print(f"[WARNING] Failed to extract features from {url}: {str(e)}")
        
        # Extract from new threats today
        links_new_today = data.get('data', {}).get('links_new_today', [])
        for url in links_new_today:
            try:
                features = extractor.extract_features(url)
                X.append(features)
                y.append(1)  # All are phishing
            except Exception as e:
                print(f"[WARNING] Failed to extract features from {url}: {str(e)}")
        
        # Extract from tracked threats
        tracked_threats = data.get('data', {}).get('tracked_threats', [])
        for threat in tracked_threats:
            url = threat.get('url', '')
            severity = threat.get('severity', 0)
            if url and severity >= 50:  # Only high severity threats
                try:
                    features = extractor.extract_features(url)
                    X.append(features)
                    y.append(1)  # Phishing
                except Exception as e:
                    print(f"[WARNING] Failed to extract features from {url}: {str(e)}")
        
        if X:
            print(f"[OK] Extracted features from {len(X)} URLs in threat database JSON")
            return np.array(X), np.array(y)
    
    except Exception as e:
        print(f"[ERROR] Failed to load threat database JSON: {str(e)}")
    
    return None, None


def load_threat_tracking_db(db_path='threat_tracking.db'):
    """Load phishing URLs from SQLite threat tracking database"""
    extractor = URLFeatureExtractor()
    X = []
    y = []
    
    if not os.path.exists(db_path):
        print(f"[WARNING] Threat tracking database not found: {db_path}")
        return None, None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\nExtracting features from threat tracking database...")
        
        # Get all incidents with severity >= 50 (table is 'incidents', not 'threats')
        cursor.execute("""
            SELECT url, severity FROM incidents 
            WHERE severity >= 50 AND status = 'open'
        """)
        
        rows = cursor.fetchall()
        for url, severity in rows:
            try:
                features = extractor.extract_features(url)
                X.append(features)
                y.append(1)  # All are phishing
            except Exception as e:
                print(f"[WARNING] Failed to extract features from {url}: {str(e)}")
        
        conn.close()
        
        if X:
            print(f"[OK] Extracted features from {len(X)} URLs in threat tracking DB")
            return np.array(X), np.array(y)
    
    except Exception as e:
        print(f"[ERROR] Failed to load threat tracking database: {str(e)}")
    
    return None, None

def load_seed_urls(seed_csv='data/seed_urls.csv'):
    """Load seed URLs from CSV dataset"""
    loader = URLDatasetLoader(seed_csv)
    
    if not loader.load_dataset():
        print("[WARNING] Failed to load seed dataset")
        return None, None
    
    extractor = URLFeatureExtractor()
    X = []
    y = []
    
    # Extract features from seed URLs
    print("\nExtracting features from seed dataset...")
    for url_record in loader.get_all_urls():
        url = url_record['URL']
        label = url_record['Label']
        
        try:
            features = extractor.extract_features(url)
            X.append(features)
            # 0 for legitimate, 1 for phishing
            y.append(0 if label == 'Legitimate' else 1)
        except Exception as e:
            print(f"[WARNING] Failed to extract features from {url}: {str(e)}")
    
    if X:
        print(f"[OK] Extracted features from {len(X)} URLs")
        return np.array(X), np.array(y)
    
    return None, None

def generate_training_data(n_samples=1000, seed_data=None):

    """
    Generate synthetic training data, optionally combining with seed data
    In production, use real labeled datasets
    """
    extractor = URLFeatureExtractor()
    X = []
    y = []
    
    # Use seed data if available
    if seed_data is not None:
        seed_X, seed_y = seed_data
        X.extend(seed_X.tolist())
        y.extend(seed_y.tolist())
        print(f"[OK] Added {len(seed_X)} URLs from seed dataset")
    
    # Legitimate URLs
    legitimate_urls = [
        'https://www.google.com',
        'https://www.github.com/user/repo',
        'https://www.stackoverflow.com/questions',
        'https://www.wikipedia.org/wiki/Python',
        'https://www.amazon.com/s?k=laptop',
        'https://www.linkedin.com/in/profile',
        'https://www.facebook.com/user',
        'https://www.instagram.com/user',
        'https://www.twitter.com/user/status',
        'https://www.youtube.com/watch?v=video',
    ]
    
    # Phishing URLs
    phishing_urls = [
        'http://192.168.1.1/login',
        'https://secure-paypal.tk/verify',
        'http://www.secure-verify-amazon-login.xyz/account',
        'https://bit.ly/secure-login-verify',
        'http://user:password@legitimate-bank.com/login',
        'https://www-paypal.com-verify-account.tk/update',
        'http://login-secure-update.verify-account.confirm.xyz',
        'https://amazon-verify.com.xyz.net/confirm',
        'https://apple-security-verify-account.ml/login',
        'http://verify-free-update-secure-account.ga/login',
    ]
    
    # Generate more training samples by adding noise
    for _ in range(n_samples // len(legitimate_urls)):
        for url in legitimate_urls:
            features = extractor.extract_features(url)
            X.append(features)
            y.append(0)  # Legitimate
    
    for _ in range(n_samples // len(phishing_urls)):
        for url in phishing_urls:
            features = extractor.extract_features(url)
            X.append(features)
            y.append(1)  # Phishing
    
    return np.array(X), np.array(y)

import pandas as pd

def load_kaggle_dataset(csv_path='data/kaggle_dataset/Phishing_Legitimate_full.csv'):
    """
    Load and map Kaggle dataset features to our model's feature space.
    Source: https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning
    """
    if not os.path.exists(csv_path):
        # Fallback to recursively finding the file in data/
        found = False
        for root, dirs, files in os.walk('data'):
            if 'Phishing_Legitimate_full.csv' in files:
                csv_path = os.path.join(root, 'Phishing_Legitimate_full.csv')
                found = True
                break
        if not found:
            print(f"[WARNING] Kaggle dataset not found at {csv_path}")
            return None, None
            
    try:
        print(f"Loading Kaggle dataset from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Initialize feature matrix with zeros (19 features)
        # We will map available features and leave others as 0
        n_samples = len(df)
        X = np.zeros((n_samples, 19))
        
        # Map features
        # 1. Has IP Address (IpAddress: 1 if IP used)
        X[:, 0] = df['IpAddress']
        
        # 2. Has @ Symbol (AtSymbol: 1 if present)
        X[:, 1] = df['AtSymbol']
        
        # 3. HTTPS Protocol (NoHttps: 1 if no https) -> Our feature: 0 if https (good), 1 if not (bad)
        # Dataset likely uses 1 for 'No Https' (bad). Ours returns 1 for 'No Https' (bad). Match.
        X[:, 2] = df['NoHttps']
        
        # 4. URL Length (UrlLength). Ours: >75 is suspicious(1)
        X[:, 3] = (df['UrlLength'] > 75).astype(int)
        
        # 5. Number of Subdomains (SubdomainLevel). Ours: >2 is suspicious(1)
        X[:, 4] = (df['SubdomainLevel'] > 2).astype(int)
        
        # 6. Has Hyphen in Domain (NumDashInHostname). Ours: >0 is suspicious(1)
        X[:, 5] = (df['NumDashInHostname'] > 0).astype(int)
        
        # 7. Suspicious Keywords (NumSensitiveWords). Ours: >0 is suspicious(1)
        X[:, 6] = (df['NumSensitiveWords'] > 0).astype(int)
        
        # 8. URL Shortener (Not explicitly in dataset, maybe 'TinyURL'? No col. Leave 0)
        
        # 9. Port in URL (Not explicit. Leave 0)
        
        # 10. Excess of Numbers (NumNumericChars). Ours: > 30% of length
        # We approximate using NumNumericChars / UrlLength
        # Avoid division by zero
        ratio = df['NumNumericChars'] / df['UrlLength'].replace(0, 1)
        X[:, 9] = (ratio > 0.3).astype(int)
        
        # 11. Domain Length (HostnameLength). Ours: >30 is suspicious(1)
        X[:, 10] = (df['HostnameLength'] > 30).astype(int)
        
        # 12. Multiple Dots (NumDots). Ours: >4 is suspicious(1)
        X[:, 11] = (df['NumDots'] > 4).astype(int)
        
        # 13. File Extension (Not explicit. Leave 0)
        
        # 14. Suspicious TLD (Not explicit. Leave 0)
        
        # 15. Double Slash Redirect (DoubleSlashInPath). Ours: 1 if present
        X[:, 14] = df['DoubleSlashInPath']
        
        # 16-19. Entropy/Homograph/FreeEmail (Not explicit. Leave 0)
        
        # Labels: Kaggle dataset uses 1 for Phishing, 0 for Legitimate (CLASS_LABEL)
        y = df['CLASS_LABEL'].values
        
        print(f"[OK] Loaded and mapped {len(X)} samples from Kaggle dataset")
        return X, y
        
    except Exception as e:
        print(f"[ERROR] Failed to load Kaggle dataset: {e}")
        return None, None


def train_models(use_seed=False, use_threats=False, use_kaggle=False, dataset_path=None):
    """Train and save both Logistic Regression and Random Forest models
    
    Args:
        use_seed (bool): If True, load and use seed URLs from CSV dataset
        use_threats (bool): If True, load threats from JSON and SQLite databases
        use_kaggle (bool): If True, load Kaggle phishing dataset
        dataset_path (str): Optional path to custom dataset CSV
    """
    
    all_X = []
    all_y = []
    
    # Load seed data if requested
    seed_data = None
    if use_seed:
        target_csv = dataset_path if dataset_path else 'data/seed_urls.csv'
        print(f"Loading dataset from substitute source: {target_csv}...")
        seed_data = load_seed_urls(target_csv)
        if seed_data[0] is None:
            print("[WARNING] Seed dataset not available")
    
    # Load separate collections into list
    collected_X = []
    collected_y = []
    
    # 1. Seed Data
    if seed_data and seed_data[0] is not None:
         collected_X.append(seed_data[0])
         collected_y.append(seed_data[1])
         
    # 2. Threat Data
    if use_threats:
        print("\nLoading threat databases...")
        # Load from JSON snapshot
        json_data = load_threat_database_json()
        if json_data[0] is not None:
             collected_X.append(json_data[0])
             collected_y.append(json_data[1])
        
        # Load from SQLite database
        db_data = load_threat_tracking_db()
        if db_data[0] is not None:
             collected_X.append(db_data[0])
             collected_y.append(db_data[1])
    
    # 3. Kaggle Data
    if use_kaggle:
        kaggle_X, kaggle_y = load_kaggle_dataset()
        if kaggle_X is not None:
            collected_X.append(kaggle_X)
            collected_y.append(kaggle_y)
    
    # Combine real data
    real_data_X = None
    real_data_y = None
    
    if collected_X:
        real_data_X = np.vstack(collected_X)
        real_data_y = np.concatenate(collected_y)
        print(f"\n[OK] Total real data samples: {len(real_data_X)}")
    
    # Generate synthetic data (if needed or to augment)
    # If we have massive real data (like Kaggle's 10k), we might not need synthetic
    # But let's keep it for robustness if real data is small
    
    n_synthetic = 1000
    if real_data_X is not None and len(real_data_X) > 5000:
        print("Large real dataset detected. Skipping synthetic data generation.")
        X = real_data_X
        y = real_data_y
    else:
        print("\nGenerating synthetic training data...")
        # Pass collected real data as seed to generator
        combined_seed = (real_data_X, real_data_y) if real_data_X is not None else None
        X, y = generate_training_data(n_synthetic, seed_data=combined_seed)
    
    print(f"Final Dataset size: {X.shape[0]} samples")
    print(f"Features: {X.shape[1]}")
    print(f"Legitimate URLs: {np.sum(y == 0)}, Phishing URLs: {np.sum(y == 1)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Save training sample for LIME
    print("\n" + "="*60)
    print("Saving Training Sample for LIME...")
    print("="*60)
    
    # Ensure models directory exists
    if not os.path.exists('models'):
        os.makedirs('models')
        
    np.save('models/training_sample.npy', X_train[:500])
    print(f"[OK] Saved {len(X_train[:500])} training samples to models/training_sample.npy")
    
    print("\n" + "="*60)
    print("Training Logistic Regression Model...")
    print("="*60)
    
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    
    lr_pred = lr_model.predict(X_test)
    lr_accuracy = accuracy_score(y_test, lr_pred)
    lr_precision = precision_score(y_test, lr_pred)
    lr_recall = recall_score(y_test, lr_pred)
    lr_f1 = f1_score(y_test, lr_pred)
    
    print(f"Accuracy:  {lr_accuracy:.4f}")
    print(f"Precision: {lr_precision:.4f}")
    print(f"Recall:    {lr_recall:.4f}")
    print(f"F1-Score:  {lr_f1:.4f}")
    
    print("\n" + "="*60)
    print("Training Random Forest Model...")
    print("="*60)
    
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=15)
    rf_model.fit(X_train, y_train)
    
    rf_pred = rf_model.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    rf_precision = precision_score(y_test, rf_pred)
    rf_recall = recall_score(y_test, rf_pred)
    rf_f1 = f1_score(y_test, rf_pred)
    
    print(f"Accuracy:  {rf_accuracy:.4f}")
    print(f"Precision: {rf_precision:.4f}")
    print(f"Recall:    {rf_recall:.4f}")
    print(f"F1-Score:  {rf_f1:.4f}")
    
    # XGBoost Model
    print("\n" + "="*60)
    print("Training XGBoost Model...")
    print("="*60)
    
    xgb_model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )
    xgb_model.fit(X_train, y_train)
    
    xgb_pred = xgb_model.predict(X_test)
    xgb_accuracy = accuracy_score(y_test, xgb_pred)
    xgb_precision = precision_score(y_test, xgb_pred)
    xgb_recall = recall_score(y_test, xgb_pred)
    xgb_f1 = f1_score(y_test, xgb_pred)
    
    print(f"Accuracy:  {xgb_accuracy:.4f}")
    print(f"Precision: {xgb_precision:.4f}")
    print(f"Recall:    {xgb_recall:.4f}")
    print(f"F1-Score:  {xgb_f1:.4f}")
    
    # Ensemble Performance
    print("\n" + "="*60)
    print("Ensemble Performance (Average of LR, RF, XGB):")
    print("="*60)
    
    # Get probabilities from all models
    lr_proba = lr_model.predict_proba(X_test)[:, 1]
    rf_proba = rf_model.predict_proba(X_test)[:, 1]
    xgb_proba = xgb_model.predict_proba(X_test)[:, 1]
    
    # Average ensemble
    ensemble_proba = (lr_proba + rf_proba + xgb_proba) / 3
    ensemble_pred = (ensemble_proba >= 0.5).astype(int)
    
    ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
    ensemble_precision = precision_score(y_test, ensemble_pred)
    ensemble_recall = recall_score(y_test, ensemble_pred)
    ensemble_f1 = f1_score(y_test, ensemble_pred)
    
    print(f"Accuracy:  {ensemble_accuracy:.4f}")
    print(f"Precision: {ensemble_precision:.4f}")
    print(f"Recall:    {ensemble_recall:.4f}")
    print(f"F1-Score:  {ensemble_f1:.4f}")
    
    # Feature importance for Random Forest
    print("\n" + "="*60)
    print("Top 5 Most Important Features (Random Forest):")
    print("="*60)
    
    extractor = URLFeatureExtractor()
    feature_names = extractor.get_feature_names()
    importance_indices = np.argsort(rf_model.feature_importances_)[::-1][:5]
    
    for idx in importance_indices:
        importance = rf_model.feature_importances_[idx]
        print(f"{feature_names[idx]:30s}: {importance:.4f}")
    
    # Feature importance for XGBoost
    print("\n" + "="*60)
    print("Top 5 Most Important Features (XGBoost):")
    print("="*60)
    
    xgb_importance_indices = np.argsort(xgb_model.feature_importances_)[::-1][:5]
    
    for idx in xgb_importance_indices:
        importance = xgb_model.feature_importances_[idx]
        print(f"{feature_names[idx]:30s}: {importance:.4f}")
    
    # Save models
    print("\n" + "="*60)
    print("Saving Models...")
    print("="*60)
    
    with open('models/lr_model.pkl', 'wb') as f:
        pickle.dump(lr_model, f)
    print("[OK] Logistic Regression model saved to models/lr_model.pkl")
    
    with open('models/rf_model.pkl', 'wb') as f:
        pickle.dump(rf_model, f)
    print("[OK] Random Forest model saved to models/rf_model.pkl")
    
    with open('models/xgb_model.pkl', 'wb') as f:
        pickle.dump(xgb_model, f)
    print("[OK] XGBoost model saved to models/xgb_model.pkl")
    
    # Save feature extractor
    with open('models/feature_extractor.pkl', 'wb') as f:
        pickle.dump(extractor, f)
    print("[OK] Feature extractor saved to models/feature_extractor.pkl")
    
    print("\n" + "="*60)
    print("Model Training Complete!")
    print("="*60)

if __name__ == "__main__":
    # Check for command line flags
    use_seed = '--use-seed' in sys.argv
    use_threats = '--use-threats' in sys.argv
    use_kaggle = '--kaggle' in sys.argv or '--use-kaggle' in sys.argv
    use_all = '--all' in sys.argv
    
    dataset_path = None
    for arg in sys.argv:
        if arg.startswith('--dataset='):
            dataset_path = arg.split('=')[1]
            use_seed = True # Implicitly enable seed usage if dataset provided

    if use_all:
        print("[INFO] Running with ALL data sources (seed + threats + kaggle)...")
        train_models(use_seed=True, use_threats=True, use_kaggle=True, dataset_path=dataset_path)
    elif use_kaggle:
        print("[INFO] Running with Kaggle dataset...")
        train_models(use_seed=use_seed, use_threats=use_threats, use_kaggle=True, dataset_path=dataset_path)
    elif use_threats:
        print("[INFO] Running with threat databases...")
        train_models(use_seed=use_seed, use_threats=True, use_kaggle=False, dataset_path=dataset_path)
    elif use_seed:
        print("[INFO] Running with seed dataset...")
        train_models(use_seed=True, use_threats=False, use_kaggle=False, dataset_path=dataset_path)
    else:
        print("[INFO] Running with synthetic data only...")
        print("[TIP] Available flags:")
        print("       --use-seed    : Include seed URLs from data/seed_urls.csv")
        print("       --dataset=PATH: Specify custom dataset path (implies --use-seed)")
        print("       --use-threats : Include URLs from threat databases")
        print("       --kaggle      : Include Kaggle dataset (Phishing_Legitimate_full.csv)")
        print("       --all         : Include ALL data sources")
        train_models(use_seed=False, use_threats=False, use_kaggle=False)
