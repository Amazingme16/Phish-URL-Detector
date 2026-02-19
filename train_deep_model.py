"""
Deep Learning Training Script for Phishing URL Detection
Trains a Character-Level CNN + LSTM model
"""

import os
import sys
import numpy as np
import pandas as pd
import pickle
import json
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, Conv1D, GlobalMaxPooling1D, LSTM, Dropout, Input
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from url_dataset_loader import URLDatasetLoader

# Configuration
MAX_LEN = 150  # Maximum URL length to consider
MAX_CHARS = 1000  # Size of vocabulary (characters)
EMBEDDING_DIM = 50
BATCH_SIZE = 32
EPOCHS = 5

def load_data(quick_run=False):
    """Load data from available sources"""
    urls = []
    labels = []
    
    print("Loading data...")
    
    # 1. Load PhishTank (validated online)
    pt_path = 'data/verified_online.csv'
    if os.path.exists(pt_path):
        try:
            df = pd.read_csv(pt_path)
            if 'url' in df.columns:
                target_urls = df['url'].values
                # Limit for efficiency if needed
                limit = 2000 if quick_run else 10000
                target_urls = target_urls[:limit]
                urls.extend(target_urls)
                labels.extend([1] * len(target_urls))
                print(f"Loaded {len(target_urls)} URLs from PhishTank")
        except Exception as e:
            print(f"Error loading PhishTank: {e}")
            
    # 2. Load Kaggle Dataset
    ka_path = 'data/kaggle_dataset/Phishing_Legitimate_full.csv'
    # Try recursive search if not found directly
    if not os.path.exists(ka_path):
        for root, dirs, files in os.walk('data'):
            if 'Phishing_Legitimate_full.csv' in files:
                ka_path = os.path.join(root, 'Phishing_Legitimate_full.csv')
                break
                
    if os.path.exists(ka_path):
        try:
            df = pd.read_csv(ka_path)
            # Kaggle has features, but we need raw URLs if available?
            # Actually this specific Kaggle dataset might NOT have raw URLs, only features.
            # Let's check columns.
            # If no raw URLs, we can't use it for DL char-level training easily without reconstruction
            # (which is inaccurate).
            # We will skip if no 'url' column.
            if 'url' in df.columns or 'URL' in df.columns:
                col = 'url' if 'url' in df.columns else 'URL'
                lbl_col = 'CLASS_LABEL' if 'CLASS_LABEL' in df.columns else 'Label'
                
                # Check if it has URLs
                sample = df[col].iloc[0] if not df.empty else ""
                if isinstance(sample, str) and (sample.startswith('http') or 'www' in sample):
                     k_urls = df[col].values
                     k_labels = df[lbl_col].values
                     
                     limit = 2000 if quick_run else 20000
                     urls.extend(k_urls[:limit])
                     labels.extend(k_labels[:limit])
                     print(f"Loaded {len(k_urls[:limit])} URLs from Kaggle dataset")
            else:
                 print("Kaggle dataset does not contain raw URLs, skipping for DL training.")
        except Exception as e:
            print(f"Error loading Kaggle dataset: {e}")

    # 3. Load Seed Data
    seed_path = 'data/seed_urls.csv'
    if os.path.exists(seed_path):
        try:
            loader = URLDatasetLoader(seed_path)
            if loader.load_dataset():
                seed_urls = loader.get_all_urls()
                for record in seed_urls:
                    urls.append(record['URL'])
                    labels.append(1 if record['Label'] == 'Phishing' else 0)
                print(f"Loaded {len(seed_urls)} URLs from seed data")
        except Exception as e:
            print(f"Error loading seed data: {e}")
            
    # 4. Generate Synthetic Data if total is small
    if len(urls) < 1000:
        print("Dataset too small, generating synthetic data...")
        legit_base = ['google.com', 'facebook.com', 'amazon.com', 'wikipedia.org', 'github.com']
        phish_base = ['secure-login.com', 'update-account.net', 'verify-wallet.xyz', 'free-crypto.tk']
        
        for _ in range(500):
            import random
            base = random.choice(legit_base)
            urls.append(f"https://www.{base}/path/{random.randint(100,999)}")
            labels.append(0)
            
            base = random.choice(phish_base)
            urls.append(f"http://{base}/login?id={random.randint(1000,9999)}")
            labels.append(1)
            
    return np.array(urls), np.array(labels)

def train_deep_model(quick_run=False):
    """Train the Deep Learning model"""
    
    # 1. Prepare Data
    X_raw, y = load_data(quick_run)
    print(f"Total samples: {len(X_raw)}")
    
    if len(X_raw) == 0:
        print("No data found! Cannot train.")
        return

    # 2. Tokenize (Character Level)
    print("Tokenizing URLs...")
    tokenizer = Tokenizer(num_words=MAX_CHARS, char_level=True, lower=True)
    tokenizer.fit_on_texts(X_raw)
    
    # Save tokenizer
    if not os.path.exists('models'):
        os.makedirs('models')
    with open('models/dl_tokenizer.pkl', 'wb') as f:
        pickle.dump(tokenizer, f)
    print("Saved tokenizer to models/dl_tokenizer.pkl")
    
    # Convert to sequences
    sequences = tokenizer.texts_to_sequences(X_raw)
    X = pad_sequences(sequences, maxlen=MAX_LEN)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3. Build Model
    print("Building Model...")
    model = Sequential([
        Input(shape=(MAX_LEN,)),
        Embedding(MAX_CHARS, EMBEDDING_DIM),
        Conv1D(128, 5, activation='relu'),
        GlobalMaxPooling1D(),
        Dropout(0.5), # Regularization
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.summary()
    
    # 4. Train
    print("Training...")
    epochs = 2 if quick_run else EPOCHS
    model.fit(X_train, y_train, 
              batch_size=BATCH_SIZE, 
              epochs=epochs, 
              validation_data=(X_test, y_test))
    
    # 5. Evaluate
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {accuracy:.4f}")
    
    # 6. Save
    model.save('models/deep_url_model.keras') # New Keras format
    # Also save as H5 for compatibility if needed, but .keras is preferred in TF 2.x
    model.save('models/deep_url_model.h5')
    print("Saved model to models/deep_url_model.keras")

if __name__ == "__main__":
    quick = '--quick' in sys.argv
    train_deep_model(quick)
