# P_URL_D Project Snapshot
**Date Saved:** December 4, 2025
**Project Version:** 2.0 (PhishSage Enhanced)

---

## Project Overview

**P_URL_D (Phishing URL Detector)** - A web-based phishing URL detection system combining machine learning with advanced heuristics from PhishSage.

### Key Stats:
- **Detection Features:** 19 (15 original + 6 PhishSage features)
- **Models:** Logistic Regression + Random Forest Ensemble
- **Accuracy:** 100% on training data
- **Framework:** Flask + Scikit-learn
- **Interface:** Web-based (HTML/CSS/JavaScript)

---

## Project Structure

```
c:\Users\hp\Desktop\P_URL_D/
├── app.py                          # Flask web application
├── train_model.py                  # Model training script
├── url_features.py                 # Feature extraction (19 features)
├── terminal_app.py                 # Terminal interface
├── requirements.txt                # Python dependencies
├── PHISHSAGE_INTEGRATION.md        # Integration progress tracker
├── PROJECT_SNAPSHOT.md             # This file
├── README.md                       # Project documentation
│
├── models/                         # Trained ML models
│   ├── lr_model.pkl               # Logistic Regression model
│   ├── rf_model.pkl               # Random Forest model
│   └── feature_extractor.pkl      # URLFeatureExtractor instance
│
├── static/                        # Web assets
│   ├── style.css                 # Styling (2-column layout)
│   └── script.js                 # Frontend JavaScript
│
├── templates/                    # HTML templates
│   └── index.html               # Main web interface
│
└── venv/                        # Python virtual environment
    └── Scripts/
        └── python.exe           # Virtual environment Python
```

---

## Recent Changes (Session: Dec 4, 2025)

### Features Added:
1. ✅ Shannon Entropy Detection (Feature 16)
2. ✅ Unicode Homograph Detection (Feature 17)
3. ✅ Subdomain Entropy Detection (Feature 18)
4. ✅ Expanded Suspicious Keywords (78+ keywords)
5. ✅ Expanded Suspicious TLDs (26+ TLDs)
6. ✅ Free Email Domain Detection (Feature 19)

### UI Changes:
- ✅ 2-column layout: Input on LEFT, Results on RIGHT
- ✅ Loading spinner displays on RIGHT side
- ✅ Responsive design for mobile devices

### Files Modified:
- `url_features.py` - Added 6 new feature detection methods
- `templates/index.html` - Reorganized layout to 2-column grid
- `static/style.css` - Added layout container and responsive styles
- Models retrained with 19 features (100% accuracy maintained)

---

## How to Run

### Start the Web Application:
```powershell
cd C:\Users\hp\Desktop\P_URL_D
.\venv\Scripts\Activate.ps1
python app.py
```

Access at: **http://localhost:5000**

### Train/Retrain Models:
```powershell
python train_model.py
```

### Install Dependencies (if needed):
```powershell
pip install -r requirements.txt
```

---

## Current Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| flask | 2.3.3 | Web framework |
| scikit-learn | 1.7.2 | ML models |
| pandas | 2.0.3 | Data handling |
| numpy | 2.3.5 | Numerical computing |
| scipy | 1.16.3 | Scientific computing |
| joblib | 1.5.2 | Model persistence |

---

## 19 Detection Features

### Original Features (1-15):
1. IP Address Detection
2. @ Symbol Detection
3. HTTPS Protocol Check
4. URL Length Check (>75 chars)
5. Excessive Subdomains
6. Hyphen in Domain
7. Suspicious Keywords
8. URL Shortener Detection
9. Non-Standard Port Detection
10. Excessive Numbers
11. Long Domain (>30 chars)
12. Excessive Dots (>4)
13. File Extension in Domain
14. Suspicious TLD
15. Double Slash Redirect

### PhishSage Features (16-19):
16. **High Domain Entropy** - Detects obfuscated domains (entropy > 3.5)
17. **Unicode Homograph** - Catches lookalike Unicode characters
18. **High Subdomain Entropy** - Suspicious subdomain patterns (entropy > 3.0)
19. **Free Email Domain** - Detects free email provider usage

### Expanded Lists:
- **Suspicious Keywords:** 78+ terms (banking, tech, phishing actions)
- **Suspicious TLDs:** 26+ domains (.tk, .ml, .pw, .ws, .zip, .download, etc.)
- **URL Shorteners:** 15+ services (bit.ly, tinyurl, is.gd, etc.)
- **Free Email Domains:** 25+ providers (Gmail, Yahoo, ProtonMail, etc.)

---

## Model Performance Metrics

```
Training Data: 2000 URLs (1000 legitimate, 1000 phishing)

Performance:
✓ Accuracy:  100.00%
✓ Precision: 100.00%
✓ Recall:    100.00%
✓ F1-Score:  100.00%

Top 5 Important Features (Random Forest):
1. file_extension_in_domain      : 25.10%
2. hyphen_in_domain              : 20.63%
3. suspicious_tld                : 11.18%
4. long_domain                   : 10.59%
5. no_https                      :  9.79%
```

---

## Web Interface Features

### Input Section (LEFT):
- URL input field with placeholder
- "Analyze" button
- Error message display area

### Results Section (RIGHT):
- Loading spinner (during analysis)
- URL display
- Model predictions:
  - Logistic Regression score & confidence
  - Random Forest score & confidence
- Overall assessment:
  - Final prediction (PHISHING/LEGITIMATE)
  - Risk level (HIGH/MEDIUM/LOW-MEDIUM/LOW)
  - Confidence percentage
  - Visual risk indicator
- Warning signs detected (if any)
- "How it works" info modal

---

## API Endpoints

### POST `/api/analyze`
Analyzes a URL and returns predictions

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "url": "https://example.com",
  "status": "success",
  "models": {
    "logistic_regression": {
      "prediction": "LEGITIMATE",
      "probability": 0.95,
      "confidence": "95.0%"
    },
    "random_forest": {
      "prediction": "LEGITIMATE",
      "probability": 0.98,
      "confidence": "98.0%"
    }
  },
  "overall": {
    "prediction": "LEGITIMATE",
    "probability": 0.965,
    "confidence": "96.5%",
    "risk_level": "LOW RISK",
    "risk_color": "#388e3c"
  },
  "warning_signs": ["suspicious_keyword", "suspicious_tld"]
}
```

### GET `/api/model-info`
Returns information about the models

### GET `/api/health`
Health check endpoint

---

## Next Steps to Enhance

### Recommended Priority Order:

1. **SSL Certificate Validation** (High Impact)
   - Check certificate age (recently issued = suspicious)
   - Verify domain match
   - Check expiration date
   
2. **WHOIS Domain Age Check** (High Impact)
   - Domains < 30 days old = suspicious
   - Expiring soon domains = suspicious

3. **Redirect Chain Detection** (Medium Impact)
   - Follow redirects and check final URL
   - Detect multi-hop obfuscation

4. **Query Parameter Analysis** (Medium Impact)
   - Detect credential theft attempts
   - Suspicious parameter patterns

5. **Path-based Detection** (Lower Priority)
   - Common phishing paths (/login, /verify, /update)
   - Encoded characters in path

---

## Development Notes

### Feature Extraction Process:
1. URL is parsed into components (domain, path, port, etc.)
2. Each of 19 features is extracted and returns 0 or 1
3. Feature vector is passed to trained models
4. Models output probability scores
5. Average of both models determines final prediction

### Model Ensemble:
- Logistic Regression: Fast, interpretable baseline
- Random Forest: Ensemble of decision trees for better generalization
- Final prediction: Average of both model probabilities

### Data Generation:
- Training data generated synthetically using heuristics
- 2000 samples: 1000 legitimate, 1000 phishing URLs
- 15-50 legitimate domain patterns
- Multiple phishing patterns per feature

---

## Performance Optimizations

- Models loaded once on app startup (pickle files)
- Feature extraction is lightweight (no external API calls)
- Web interface uses client-side JavaScript
- CSS animations are GPU-accelerated

---

## Security Considerations

⚠️ **Important Notes:**
- This is a demonstration/educational tool
- ML models trained on synthetic data
- 100% accuracy may not reflect real-world performance
- Use in combination with other security measures
- Regular model retraining recommended with real-world data

---

## Backup/Recovery

**Key Files to Backup:**
- `models/lr_model.pkl` - Logistic Regression model
- `models/rf_model.pkl` - Random Forest model
- `models/feature_extractor.pkl` - Feature extractor
- `url_features.py` - Feature extraction logic
- `app.py` - Web application

**To Restore:**
1. Copy backed-up model files to `models/` directory
2. Run `python app.py`
3. Models will be loaded from pickle files

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Initial | 15 original features, basic ML models |
| 1.5 | Dec 4 AM | 2-column UI layout |
| 2.0 | Dec 4 PM | 6 PhishSage features added (19 total) |

---

## Contact/Support Notes

- If models need retraining: `python train_model.py`
- If features need updating: Edit `url_features.py`, then retrain
- Models use pickle format (Python serialization)
- Web interface is responsive (mobile-friendly)

---

**Project Status:** ✅ ACTIVE & FUNCTIONAL
**Last Tested:** December 4, 2025
**Next Review:** As needed
