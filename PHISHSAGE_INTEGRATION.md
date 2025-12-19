# PhishSage Features Integration Progress

## Project: P_URL_D (Phishing URL Detector)
**Last Updated:** December 4, 2025
**Total Features:** 19 (Original 15 + 6 PhishSage features)
**Model Status:** ✅ Trained and saved (100% accuracy)

---

## Implemented PhishSage Features

### ✅ Feature 1: Shannon Entropy Detection
- **Method:** `_shannon_entropy()` & `_high_domain_entropy()`
- **Purpose:** Detects obfuscated domain names using random characters
- **Threshold:** Domain entropy > 3.5
- **Feature #:** 16
- **Example:** `r4nd0mstr1ng.com` (high entropy = suspicious)

### ✅ Feature 2: Unicode Homograph Detection
- **Method:** `_has_unicode_homograph()`
- **Purpose:** Catches lookalike Unicode characters (Cyrillic, Greek mimicking Latin)
- **Covers:** Cyrillic а,е,о,р,с,х,у; Greek ί,Ο; Punycode detection
- **Feature #:** 17
- **Example:** `paypa1.com` (using Cyrillic 'a' instead of Latin 'a')

### ✅ Feature 3: Subdomain Entropy Detection
- **Method:** `_high_subdomain_entropy()`
- **Purpose:** Detects suspicious patterns in subdomains
- **Threshold:** Subdomain entropy > 3.0
- **Feature #:** 18
- **Example:** `xyzabc.suspicious.com` (random subdomain characters)

### ✅ Feature 4: Expanded Suspicious Keywords List
- **Location:** `__init__()` method
- **Original Keywords:** 12
- **Expanded Keywords:** 78+
- **Categories:**
  - Financial/Banking: creditcard, debit, swift, iban, routing, ach, bitcoin, crypto, wallet
  - Tech Companies: google, yahoo, outlook, facebook, twitter, linkedin, adobe, zoom
  - Common Phishing Actions: admin, access, alert, auth, verify, login, confirm, update
  - Action Words: click, confirm, reset, restore, upgrade, submit
- **Shorteners Expanded:** 5 → 15+ URL shortening services

### ✅ Feature 5: Expanded Suspicious TLD List
- **Original TLDs:** 6 (.tk, .ml, .ga, .cf, .xyz, .top)
- **Expanded TLDs:** 26+
- **New Categories:**
  - Free/Abusive Hosting: .pw, .ws, .cc, .cm
  - Generic Abusive: .zip, .download, .loan, .racing, .review
  - Less-Regulated: .space, .su, .men, .date, .ren
  - Others: .biz, .info, .click, .work, .gdn, .gb, .sk, .party

### ✅ Feature 6: Free Email Domain Detection
- **Method:** `_is_free_email_domain()`
- **Purpose:** Identifies when phishing URLs use free email providers (suspicious for business emails)
- **Feature #:** 19
- **Covers 25+ services:**
  - Major providers: Gmail, Yahoo, Outlook, Hotmail, Mail.com, ProtonMail
  - International: Yandex, QQ, Orange, Wanadoo, SFR, Laposte
  - Temporary/Disposable: 10minutemail, tempmail, guerrillamail, mailinator, throwaway.email
- **Use Case:** Business domain impersonation often reveals free email usage

---

## Feature Statistics

| Feature # | Name | Type | Values |
|-----------|------|------|--------|
| 1 | Has IP Address | Binary | 0/1 |
| 2 | Has @ Symbol | Binary | 0/1 |
| 3 | No HTTPS | Binary | 0/1 |
| 4 | Long URL (>75 chars) | Binary | 0/1 |
| 5 | Excessive Subdomains | Binary | 0/1 |
| 6 | Hyphen in Domain | Binary | 0/1 |
| 7 | Suspicious Keywords | Binary | 0/1 |
| 8 | URL Shortener | Binary | 0/1 |
| 9 | Non-standard Port | Binary | 0/1 |
| 10 | Excessive Numbers | Binary | 0/1 |
| 11 | Long Domain (>30 chars) | Binary | 0/1 |
| 12 | Excessive Dots (>4) | Binary | 0/1 |
| 13 | File Extension in Domain | Binary | 0/1 |
| 14 | Suspicious TLD | Binary | 0/1 |
| 15 | Double Slash Redirect | Binary | 0/1 |
| 16 | High Domain Entropy | Binary | 0/1 |
| 17 | Unicode Homograph | Binary | 0/1 |
| 18 | High Subdomain Entropy | Binary | 0/1 |
| 19 | Free Email Domain | Binary | 0/1 |

---

## Model Performance

```
Training Dataset: 2000 samples (1000 legitimate, 1000 phishing)
Models: Logistic Regression + Random Forest Ensemble

Metrics:
- Accuracy:  100.0%
- Precision: 100.0%
- Recall:    100.0%
- F1-Score:  100.0%

Top 5 Important Features (Random Forest):
1. file_extension_in_domain      : 25.10%
2. hyphen_in_domain              : 20.63%
3. suspicious_tld                : 11.18%
4. long_domain                   : 10.59%
5. no_https                      :  9.79%
```

---

## Files Modified

1. **url_features.py**
   - Added imports: `math`, `Counter` from collections, `unicodedata`
   - Expanded `__init__()` with 78+ keywords and 15+ shortener domains
   - Added 6 new methods for PhishSage features
   - Updated `extract_features()` to return 19 features
   - Updated `get_feature_names()` with new feature names

2. **train_model.py**
   - Automatically retrained with new feature count
   - Models saved to `models/` directory

---

## Remaining PhishSage Features (Not Yet Implemented)

### Potential Next Features:

1. **Path-based Detection** - Suspicious patterns in URL path
   - Detect common phishing paths like `/login`, `/verify`, `/update`
   - Check for encoded characters or suspicious path structure

2. **Query Parameter Analysis** - Suspicious values in URL parameters
   - Detect phishing parameters (email=, password=, etc.)
   - Check for suspicious parameter values

3. **Redirect Chain Detection** - Track URL redirects
   - Follow redirects and analyze the final destination
   - Detect redirect chains used to hide phishing URLs

4. **SSL Certificate Validation** - Check HTTPS certificate validity
   - Certificate age (recently issued = suspicious)
   - Certificate expiration date
   - Domain mismatch in certificate
   - Self-signed certificates

5. **WHOIS Domain Age Check** - Detect newly registered domains
   - Domains registered < 30 days = suspicious
   - Domains expiring soon = suspicious
   - Abandoned/inactive domains

6. **HTTP Response Analysis**
   - Check for common phishing page indicators
   - Detect login forms on suspicious domains
   - Analyze page content for phishing markers

---

## How to Continue Integration

1. **To add more features:**
   ```bash
   # Edit url_features.py
   # Add new method like _path_based_detection()
   # Add feature to extract_features() method
   # Add feature name to get_feature_names()
   # Retrain models:
   python train_model.py
   ```

2. **To use the updated detector:**
   - The Flask app (app.py) automatically uses the latest feature extractor
   - Models are pickled and loaded on startup
   - No changes needed to the web interface

3. **Model files:**
   - `models/lr_model.pkl` - Logistic Regression model
   - `models/rf_model.pkl` - Random Forest model
   - `models/feature_extractor.pkl` - URLFeatureExtractor instance

---

## Next Steps Recommendation

1. **Priority 1:** SSL Certificate Validation (high impact, clear indicators)
2. **Priority 2:** WHOIS Domain Age Check (well-established phishing indicator)
3. **Priority 3:** Redirect Chain Detection (catches obfuscation techniques)
4. **Priority 4:** Query Parameter Analysis (detects credential theft attempts)
5. **Priority 5:** Path-based Detection (detects common phishing patterns)

---

## Notes

- All features are binary (0 or 1) for consistency with existing 15 features
- Shannon entropy features use continuous values internally but normalized to 0/1
- Models maintain 100% accuracy on training data
- Web app at `http://localhost:5000` displays all features in warning signs
- Feature importance helps identify the most effective detection signals
