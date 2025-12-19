#!/usr/bin/env python
"""Test script for Link Threats Detector"""

from link_threats_detector import LinkThreatsDetector

detector = LinkThreatsDetector()

test_urls = [
    ('https://paypa1.com/login', 'Typosquatting'),
    ('https://amazon-verify.xyz/account/update', 'Brand Impersonation'),
    ('https://bank.com/login?redirect=https://evil.com', 'Redirect Chain'),
    ('http://192.168.1.1/admin/shell.exe', 'IP + Malicious Pattern'),
    ('https://example.tk/phishing', 'Suspicious TLD'),
]

print("=" * 80)
print("LINK THREATS DETECTOR - COMPREHENSIVE TEST")
print("=" * 80)

for url, description in test_urls:
    result = detector.detect_all_threats(url)
    print(f"\nTest: {description}")
    print(f"URL: {url}")
    print(f"Threat Level: {result['threat_level'].upper()}")
    print(f"Threat Score: {result['threat_score']}/100")
    print(f"Threats Found: {', '.join(result['threats_found']) if result['threats_found'] else 'None'}")

print("\n" + "=" * 80)
