"""
Test Flask App Integration with Seed Dataset Loader
Tests API endpoints and seed dataset availability
"""

import json
import sys
from app import app, seed_dataset_loaded, seed_dataset_info


def test_flask_app_initialization():
    """Test that Flask app initializes with seed dataset"""
    print("\n" + "="*70)
    print("TEST 1: FLASK APP INITIALIZATION")
    print("="*70)
    
    print(f"[OK] Flask app created successfully")
    print(f"[OK] Seed dataset loaded: {seed_dataset_loaded}")
    print(f"[OK] Dataset info: {seed_dataset_info}")
    
    assert seed_dataset_loaded, "Seed dataset should be loaded"
    assert seed_dataset_info['total_urls'] == 40, "Should have 40 URLs"
    assert seed_dataset_info['phishing_count'] == 30, "Should have 30 phishing URLs"
    assert seed_dataset_info['legitimate_count'] == 10, "Should have 10 legitimate URLs"
    
    print("\n[PASS] Flask app initialized correctly")
    return True


def test_seed_dataset_endpoint():
    """Test /api/seed-dataset endpoint"""
    print("\n" + "="*70)
    print("TEST 2: SEED DATASET API ENDPOINT")
    print("="*70)
    
    client = app.test_client()
    response = client.get('/api/seed-dataset')
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"[OK] Endpoint returned status 200")
    
    data = json.loads(response.data)
    print(f"[OK] Response parsed successfully")
    
    assert data['status'] == 'loaded', f"Expected 'loaded' status, got {data['status']}"
    print(f"[OK] Status: {data['status']}")
    
    # Check dataset info
    info = data['info']
    assert info['total_urls'] == 40, f"Expected 40 URLs, got {info['total_urls']}"
    print(f"[OK] Total URLs: {info['total_urls']}")
    
    assert info['phishing_count'] == 30, f"Expected 30 phishing, got {info['phishing_count']}"
    print(f"[OK] Phishing URLs: {info['phishing_count']}")
    
    assert info['legitimate_count'] == 10, f"Expected 10 legitimate, got {info['legitimate_count']}"
    print(f"[OK] Legitimate URLs: {info['legitimate_count']}")
    
    # Check validation
    validation = data['validation']
    assert validation['total'] == 40, "All 40 URLs should be present"
    assert validation['valid'] == 40, "All 40 URLs should be valid"
    print(f"[OK] Validation: {validation['valid']}/{validation['total']} valid")
    
    # Check samples
    assert len(data['phishing_samples']) <= 3, "Should have up to 3 phishing samples"
    assert len(data['legitimate_samples']) <= 3, "Should have up to 3 legitimate samples"
    print(f"[OK] Phishing samples: {len(data['phishing_samples'])}")
    print(f"[OK] Legitimate samples: {len(data['legitimate_samples'])}")
    
    print("\n[PASS] Seed dataset endpoint working correctly")
    return True


def test_health_endpoint_with_seed():
    """Test /api/health endpoint includes seed dataset"""
    print("\n" + "="*70)
    print("TEST 3: HEALTH ENDPOINT WITH SEED DATASET")
    print("="*70)
    
    client = app.test_client()
    response = client.get('/api/health')
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"[OK] Health endpoint returned status 200")
    
    data = json.loads(response.data)
    
    assert data['status'] == 'healthy', "System should be healthy"
    print(f"[OK] System status: {data['status']}")
    
    assert data['seed_dataset_loaded'] == True, "Seed dataset should be loaded"
    print(f"[OK] Seed dataset loaded: {data['seed_dataset_loaded']}")
    
    # Check seed dataset info in health
    if 'seed_dataset' in data:
        seed_info = data['seed_dataset']
        assert seed_info['total_urls'] == 40, "Should show 40 URLs"
        print(f"[OK] Seed dataset in health: {seed_info['total_urls']} URLs")
    
    print("\n[PASS] Health endpoint includes seed dataset info")
    return True


def test_threat_database_with_seed():
    """Test threat database status alongside seed dataset"""
    print("\n" + "="*70)
    print("TEST 4: THREAT DATABASE AND SEED DATASET STATUS")
    print("="*70)
    
    client = app.test_client()
    response = client.get('/api/health')
    data = json.loads(response.data)
    
    print("Threat Database Status:")
    threat_db = data['threat_database']
    print(f"  Snapshot available: {threat_db['snapshot_available']}")
    print(f"  Cache available: {threat_db['cache_available']}")
    print(f"  Snapshot entries: {threat_db['snapshot_entries']}")
    print(f"  Cache entries: {threat_db['cache_entries']}")
    
    print("\nSeed Dataset Status:")
    print(f"  Loaded: {data['seed_dataset_loaded']}")
    if 'seed_dataset' in data:
        seed_info = data['seed_dataset']
        print(f"  Total URLs: {seed_info['total_urls']}")
        print(f"  Phishing: {seed_info['phishing_count']}")
        print(f"  Legitimate: {seed_info['legitimate_count']}")
    
    print("\n[PASS] Both threat database and seed dataset status available")
    return True


def test_model_info_endpoint():
    """Test /api/model-info endpoint"""
    print("\n" + "="*70)
    print("TEST 5: MODEL INFO ENDPOINT")
    print("="*70)
    
    client = app.test_client()
    response = client.get('/api/model-info')
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"[OK] Model info endpoint returned status 200")
    
    data = json.loads(response.data)
    
    assert data['models_loaded'], "Models should be loaded"
    print(f"[OK] Models loaded: {data['models_loaded']}")
    
    print(f"[OK] Feature count: {data['features_count']}")
    print(f"[OK] Algorithms: {', '.join(data['algorithms'])}")
    
    print("\n[PASS] Model info endpoint working")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("FLASK APP SEED DATASET INTEGRATION TEST SUITE")
    print("="*70)
    
    tests = [
        ("Flask App Initialization", test_flask_app_initialization),
        ("Seed Dataset Endpoint", test_seed_dataset_endpoint),
        ("Health Endpoint", test_health_endpoint_with_seed),
        ("Threat DB & Seed Status", test_threat_database_with_seed),
        ("Model Info Endpoint", test_model_info_endpoint),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[ERROR] Test '{test_name}' failed with error:")
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
        print("\n[SUCCESS] ALL TESTS PASSED - Flask app fully integrated with seed dataset!")
    else:
        print(f"\n[ERROR] {total_tests - total_passed} test(s) failed")
    
    print("="*70 + "\n")
    
    return total_passed == total_tests


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
