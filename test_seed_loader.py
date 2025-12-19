"""
Test URL Seed Dataset Loading and Detection
Verifies that loaded URLs are correctly detected as phishing or legitimate
"""

import pickle
from url_dataset_loader import URLDatasetLoader
from url_features import URLFeatureExtractor


def test_seed_loading():
    """Test that seed dataset loads correctly"""
    print("\n" + "="*70)
    print("TEST 1: SEED DATASET LOADING")
    print("="*70)
    
    loader = URLDatasetLoader('data/seed_urls.csv')
    assert loader.load_dataset(), "Failed to load seed dataset"
    
    info = loader.get_dataset_info()
    assert info['total_urls'] == 40, f"Expected 40 URLs, got {info['total_urls']}"
    assert info['phishing_count'] == 30, f"Expected 30 phishing, got {info['phishing_count']}"
    assert info['legitimate_count'] == 10, f"Expected 10 legitimate, got {info['legitimate_count']}"
    
    print(f"✓ Loaded {info['total_urls']} URLs")
    print(f"✓ Phishing: {info['phishing_count']}")
    print(f"✓ Legitimate: {info['legitimate_count']}")
    
    return True


def test_feature_extraction():
    """Test that features are extracted from all seed URLs"""
    print("\n" + "="*70)
    print("TEST 2: FEATURE EXTRACTION")
    print("="*70)
    
    loader = URLDatasetLoader('data/seed_urls.csv')
    loader.load_dataset()
    
    extractor = URLFeatureExtractor()
    extracted_count = 0
    
    for url_record in loader.get_all_urls():
        url = url_record['URL']
        try:
            features = extractor.extract_features(url)
            assert len(features) == 19, f"Expected 19 features, got {len(features)}"
            extracted_count += 1
        except Exception as e:
            print(f"✗ Failed to extract features from {url}: {str(e)}")
            return False
    
    print(f"✓ Extracted features from {extracted_count}/40 URLs")
    assert extracted_count == 40, f"Should extract 40 URLs, extracted {extracted_count}"
    
    return True


def test_model_detection():
    """Test that trained model can detect phishing/legitimate URLs"""
    print("\n" + "="*70)
    print("TEST 3: MODEL DETECTION")
    print("="*70)
    
    try:
        # Load trained models
        with open('models/lr_model.pkl', 'rb') as f:
            lr_model = pickle.load(f)
        print("✓ Loaded Logistic Regression model")
        
        with open('models/rf_model.pkl', 'rb') as f:
            rf_model = pickle.load(f)
        print("✓ Loaded Random Forest model")
        
    except FileNotFoundError:
        print("✗ Models not found. Run: python train_model.py --use-seed")
        return False
    
    loader = URLDatasetLoader('data/seed_urls.csv')
    loader.load_dataset()
    extractor = URLFeatureExtractor()
    
    # Test detection on sample URLs
    test_urls = [
        ('http://paypa1-login.com', 'Phishing'),
        ('https://www.paypal.com', 'Legitimate'),
        ('http://faceb00k-security.net', 'Phishing'),
        ('https://www.amazon.com', 'Legitimate'),
    ]
    
    print("\nDetecting URLs:")
    for url, expected_label in test_urls:
        features = extractor.extract_features(url)
        
        lr_pred = lr_model.predict([features])[0]
        rf_pred = rf_model.predict([features])[0]
        
        lr_label = 'Phishing' if lr_pred == 1 else 'Legitimate'
        rf_label = 'Phishing' if rf_pred == 1 else 'Legitimate'
        
        lr_match = "✓" if lr_label == expected_label else "✗"
        rf_match = "✓" if rf_label == expected_label else "✗"
        
        print(f"  {url}")
        print(f"    Expected: {expected_label}")
        print(f"    LR Model: {lr_label} {lr_match}")
        print(f"    RF Model: {rf_label} {rf_match}")
    
    return True


def test_all_seed_urls():
    """Test detection on all 40 seed URLs"""
    print("\n" + "="*70)
    print("TEST 4: DETECTION ON ALL SEED URLS")
    print("="*70)
    
    try:
        with open('models/rf_model.pkl', 'rb') as f:
            rf_model = pickle.load(f)
    except FileNotFoundError:
        print("✗ Models not found. Run: python train_model.py --use-seed")
        return False
    
    loader = URLDatasetLoader('data/seed_urls.csv')
    loader.load_dataset()
    extractor = URLFeatureExtractor()
    
    phishing_correct = 0
    legitimate_correct = 0
    phishing_total = len(loader.get_phishing_urls())
    legitimate_total = len(loader.get_legitimate_urls())
    
    # Test phishing URLs
    for url in loader.get_phishing_urls():
        features = extractor.extract_features(url)
        pred = rf_model.predict([features])[0]
        if pred == 1:  # Phishing detected
            phishing_correct += 1
    
    # Test legitimate URLs
    for url in loader.get_legitimate_urls():
        features = extractor.extract_features(url)
        pred = rf_model.predict([features])[0]
        if pred == 0:  # Legitimate detected
            legitimate_correct += 1
    
    phishing_accuracy = (phishing_correct / phishing_total) * 100 if phishing_total > 0 else 0
    legitimate_accuracy = (legitimate_correct / legitimate_total) * 100 if legitimate_total > 0 else 0
    overall_accuracy = ((phishing_correct + legitimate_correct) / 40) * 100
    
    print(f"\nPhishing URLs: {phishing_correct}/{phishing_total} correct ({phishing_accuracy:.1f}%)")
    print(f"Legitimate URLs: {legitimate_correct}/{legitimate_total} correct ({legitimate_accuracy:.1f}%)")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    
    return phishing_accuracy >= 80 and legitimate_accuracy >= 80


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("URL SEED DATASET LOADER AND DETECTOR TEST SUITE")
    print("="*70)
    
    tests = [
        ("Seed Loading", test_seed_loading),
        ("Feature Extraction", test_feature_extraction),
        ("Model Detection", test_model_detection),
        ("All Seed URLs", test_all_seed_urls),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with error:")
            print(f"  {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    total_passed = sum(1 for p in results.values() if p)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n✓ ALL TESTS PASSED - Seed dataset successfully loaded into detector!")
    else:
        print(f"\n✗ {total_tests - total_passed} test(s) failed")
    
    print("="*70 + "\n")
    
    return total_passed == total_tests


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
