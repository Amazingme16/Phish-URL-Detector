"""
Verification Script for Deep Learning Model
Loads the trained model and runs predictions on sample URLs
"""

import os
import pickle
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np

def verify_model():
    print("Verifying Deep Learning Model...")
    
    # Paths
    model_path = 'models/deep_url_model.keras'
    tokenizer_path = 'models/dl_tokenizer.pkl'
    
    if not os.path.exists(model_path):
        # Check for H5 compatibility
        model_path = 'models/deep_url_model.h5'
        if not os.path.exists(model_path):
            print(f"[ERROR] Model file not found at {model_path}")
            return
            
    if not os.path.exists(tokenizer_path):
        print(f"[ERROR] Tokenizer file not found at {tokenizer_path}")
        return
        
    try:
        # Load Model
        print(f"Loading model from {model_path}...")
        model = load_model(model_path)
        
        # Load Tokenizer
        print(f"Loading tokenizer from {tokenizer_path}...")
        with open(tokenizer_path, 'rb') as f:
            tokenizer = pickle.load(f)
            
        print("[OK] Model and Tokenizer loaded successfully")
        
        # Test URLs
        test_urls = [
            # Legitimate
            "https://www.google.com",
            "https://github.com/tensorflow/tensorflow",
            "https://stackoverflow.com/questions/12345/python-question",
            # Phishing (synthetic examples)
            "http://secure-login.paypal-verify.com.tk/account",
            "http://apple-id.verify-update.ga/login",
            "https://amazon-security-alert.xyz/confirm-details"
        ]
        
        print("\nRunning Predictions:")
        print("-" * 60)
        print(f"{'URL':<50} | {'Prob':<8} | {'Prediction'}")
        print("-" * 60)
        
        # Preprocess
        sequences = tokenizer.texts_to_sequences(test_urls)
        X_test = pad_sequences(sequences, maxlen=150)
        
        # Predict
        predictions = model.predict(X_test, verbose=0)
        
        for url, pred in zip(test_urls, predictions):
            prob = float(pred[0])
            label = "PHISHING" if prob >= 0.5 else "LEGITIMATE"
            print(f"{url[:47]:<50} | {prob:.4f}   | {label}")
            
        print("-" * 60)
        print("[OK] Verification Complete")
        
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")

if __name__ == "__main__":
    verify_model()
