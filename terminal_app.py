"""
Terminal-based Phishing URL Detector
Simple command-line interface for testing URLs
"""

import pickle
from url_features import URLFeatureExtractor

def load_models():
    """Load trained models"""
    try:
        with open('models/lr_model.pkl', 'rb') as f:
            lr_model = pickle.load(f)
        with open('models/rf_model.pkl', 'rb') as f:
            rf_model = pickle.load(f)
        with open('models/feature_extractor.pkl', 'rb') as f:
            feature_extractor = pickle.load(f)
        return lr_model, rf_model, feature_extractor
    except FileNotFoundError:
        print("❌ Models not found! Please run train_model.py first.")
        return None, None, None

def get_risk_level(probability):
    """Classify risk level based on probability"""
    if probability >= 0.75:
        return "🔴 HIGH RISK"
    elif probability >= 0.50:
        return "🟠 MEDIUM RISK"
    elif probability >= 0.25:
        return "🟡 LOW-MEDIUM RISK"
    else:
        return "🟢 LOW RISK"

def analyze_url(url, lr_model, rf_model, feature_extractor):
    """Analyze a URL and display results"""
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Extract features
    features = feature_extractor.extract_features(url)
    
    # Get predictions
    lr_pred = lr_model.predict([features])[0]
    lr_prob = lr_model.predict_proba([features])[0][1]
    
    rf_pred = rf_model.predict([features])[0]
    rf_prob = rf_model.predict_proba([features])[0][1]
    
    # Average probability
    avg_prob = (lr_prob + rf_prob) / 2
    
    print("\n" + "="*70)
    print(f"URL: {url}")
    print("="*70)
    
    print("\n📊 MODEL PREDICTIONS:")
    print("-" * 70)
    print(f"Logistic Regression: {'⚠️  PHISHING' if lr_pred == 1 else '✅ LEGITIMATE'} ({lr_prob*100:.1f}% confidence)")
    print(f"Random Forest:       {'⚠️  PHISHING' if rf_pred == 1 else '✅ LEGITIMATE'} ({rf_prob*100:.1f}% confidence)")
    
    print("\n🎯 OVERALL ASSESSMENT:")
    print("-" * 70)
    overall_pred = "PHISHING" if avg_prob >= 0.5 else "LEGITIMATE"
    print(f"Prediction: {overall_pred}")
    print(f"Risk Level: {get_risk_level(avg_prob)}")
    print(f"Confidence: {avg_prob*100:.1f}%")
    
    print("\n⚠️  WARNING SIGNS DETECTED:")
    print("-" * 70)
    feature_names = feature_extractor.get_feature_names()
    warning_signs = []
    for i, (feature_name, feature_value) in enumerate(zip(feature_names, features)):
        if feature_value == 1:
            warning_signs.append(feature_name.replace('_', ' ').title())
    
    if warning_signs:
        for i, sign in enumerate(warning_signs, 1):
            print(f"  {i}. {sign}")
    else:
        print("  No warning signs detected")
    
    print("\n" + "="*70 + "\n")

def main():
    """Main terminal interface"""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  P URL D - PHISHING URL DETECTOR (Terminal)".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    print("\n")
    
    lr_model, rf_model, feature_extractor = load_models()
    
    if not lr_model or not rf_model:
        return
    
    print("Type 'exit' to quit, 'help' for commands\n")
    
    while True:
        try:
            url = input("🔍 Enter URL to analyze (or 'exit'): ").strip()
            
            if url.lower() == 'exit':
                print("\n👋 Goodbye!\n")
                break
            elif url.lower() == 'help':
                print("\n" + "="*70)
                print("COMMANDS:")
                print("  - Enter any URL to analyze (with or without http://https://)")
                print("  - Type 'exit' to quit")
                print("  - Type 'help' to show this message")
                print("="*70 + "\n")
                continue
            elif not url:
                continue
            
            analyze_url(url, lr_model, rf_model, feature_extractor)
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
