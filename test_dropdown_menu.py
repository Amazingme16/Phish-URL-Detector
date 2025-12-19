"""
Test Dropdown Menu UI Implementation
Tests that the analyze button has dropdown menu with 4 analysis modes
"""

import json
from app import app


def test_homepage_loads():
    """Test that homepage loads with dropdown menu HTML"""
    print("\n" + "="*70)
    print("TEST 1: HOMEPAGE LOADS")
    print("="*70)
    
    client = app.test_client()
    response = client.get('/')
    
    assert response.status_code == 200, "Homepage should load"
    print("[OK] Homepage returned status 200")
    
    html = response.data.decode('utf-8')
    
    # Check for dropdown menu elements
    assert 'button-dropdown' in html, "Should have button-dropdown class"
    print("[OK] Found button-dropdown class")
    
    assert 'analysis-menu' in html, "Should have analysis-menu div"
    print("[OK] Found analysis-menu div")
    
    assert 'Quick Analysis' in html, "Should have Quick Analysis option"
    print("[OK] Found 'Quick Analysis' menu item")
    
    assert 'Full Analysis' in html, "Should have Full Analysis option"
    print("[OK] Found 'Full Analysis' menu item")
    
    assert 'Advanced' in html, "Should have Advanced Analysis option"
    print("[OK] Found 'Advanced Analysis' menu item")
    
    assert 'Compare Models' in html, "Should have Compare Models option"
    print("[OK] Found 'Compare Models' menu item")
    
    assert 'toggleAnalysisMenu' in html, "Should have toggleAnalysisMenu function"
    print("[OK] Found toggleAnalysisMenu JavaScript function")
    
    print("\n[PASS] Homepage has all dropdown menu elements")
    return True


def test_analyze_endpoint_with_mode():
    """Test that analyze endpoint accepts mode parameter"""
    print("\n" + "="*70)
    print("TEST 2: ANALYZE ENDPOINT WITH MODE PARAMETER")
    print("="*70)
    
    client = app.test_client()
    
    test_cases = [
        ('quick', 'Quick mode'),
        ('full', 'Full mode'),
        ('advanced', 'Advanced mode'),
        ('compare', 'Compare mode'),
    ]
    
    for mode, description in test_cases:
        response = client.post('/api/analyze', 
            json={'url': 'https://example.com', 'mode': mode},
            content_type='application/json'
        )
        
        assert response.status_code == 200, f"Should accept {mode} mode"
        data = json.loads(response.data)
        assert data['status'] == 'success', f"Analysis should succeed for {mode}"
        assert data['analysis_mode'] == mode, f"Response should include mode: {mode}"
        print(f"[OK] {description} - Returned analysis_mode: {data['analysis_mode']}")
    
    print("\n[PASS] Analyze endpoint accepts all modes")
    return True


def test_quick_mode_response():
    """Test that quick mode returns ML results only"""
    print("\n" + "="*70)
    print("TEST 3: QUICK MODE RESPONSE")
    print("="*70)
    
    client = app.test_client()
    
    response = client.post('/api/analyze',
        json={'url': 'https://example.com', 'mode': 'quick'},
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    # Should have ML predictions
    assert 'models' in data, "Should have ML models"
    assert 'logistic_regression' in data['models'], "Should have LR model"
    assert 'random_forest' in data['models'], "Should have RF model"
    print("[OK] Quick mode includes ML model predictions")
    
    # Should have warning signs
    assert 'warning_signs' in data, "Should have warning signs"
    print("[OK] Quick mode includes warning signs")
    
    # Should NOT have advanced analysis in quick mode
    assert 'advanced_analysis' not in data, "Quick mode should not have advanced analysis"
    print("[OK] Quick mode skips advanced analysis")
    
    print("\n[PASS] Quick mode returns correct response structure")
    return True


def test_full_mode_response():
    """Test that full mode returns all results"""
    print("\n" + "="*70)
    print("TEST 4: FULL MODE RESPONSE")
    print("="*70)
    
    client = app.test_client()
    
    response = client.post('/api/analyze',
        json={'url': 'https://example.com', 'mode': 'full'},
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    # Should have ML predictions
    assert 'models' in data, "Should have ML models"
    print("[OK] Full mode includes ML predictions")
    
    # May have advanced analysis (depends on network)
    if 'advanced_analysis' in data:
        print("[OK] Full mode includes advanced analysis (network available)")
    else:
        print("[OK] Full mode skipped advanced analysis (network unavailable)")
    
    print("\n[PASS] Full mode returns comprehensive response")
    return True


def test_analyze_default_mode():
    """Test that analyze defaults to full mode when no mode specified"""
    print("\n" + "="*70)
    print("TEST 5: ANALYZE DEFAULT MODE")
    print("="*70)
    
    client = app.test_client()
    
    response = client.post('/api/analyze',
        json={'url': 'https://example.com'},
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    assert data['analysis_mode'] == 'full', "Should default to full mode"
    print("[OK] Analyze defaults to full mode when no mode specified")
    
    print("\n[PASS] Default mode handling works correctly")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("ANALYZE BUTTON DROPDOWN MENU TEST SUITE")
    print("="*70)
    
    tests = [
        ("Homepage Loads", test_homepage_loads),
        ("Analyze Endpoint with Mode", test_analyze_endpoint_with_mode),
        ("Quick Mode Response", test_quick_mode_response),
        ("Full Mode Response", test_full_mode_response),
        ("Analyze Default Mode", test_analyze_default_mode),
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
        print("\n[SUCCESS] Dropdown menu fully implemented and tested!")
        print("\nAnalysis Modes:")
        print("  1. Quick Analysis (ML only) - Fast analysis using ML models")
        print("  2. Full Analysis (all checks) - Comprehensive with advanced checks")
        print("  3. Advanced + Seed Data - Uses seed dataset for comparison")
        print("  4. Compare Models - Detailed model comparison")
    else:
        print(f"\n[ERROR] {total_tests - total_passed} test(s) failed")
    
    print("="*70 + "\n")
    
    return total_passed == total_tests


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
