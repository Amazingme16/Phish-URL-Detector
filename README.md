# 🔐 P URL D - Phishing URL Detector

A machine learning-powered web application that detects phishing URLs using **Logistic Regression** and **Random Forest** algorithms.

## ✨ Features

- **Dual ML Models**: Combines Logistic Regression and Random Forest for accurate detection
- **15 Advanced Features**: Analyzes URL structure, patterns, and characteristics
- **Web Interface**: Clean, modern Flask web application with real-time analysis
- **Terminal App**: Command-line interface for batch testing
- **Risk Classification**: Categorizes URLs into 4 risk levels (Low, Low-Medium, Medium, High)
- **Feature Analysis**: Shows which warning signs were detected

## 📊 How It Works

### Feature Extraction (15 Features)
The system analyzes:
1. IP address in URL
2. @ symbol presence
3. HTTPS protocol usage
4. URL length (>75 chars = suspicious)
5. Excessive subdomains
6. Hyphens in domain
7. Suspicious keywords (verify, login, secure, etc.)
8. URL shortener services
9. Non-standard ports
10. Excessive numbers
11. Long domain names
12. Excessive dots
13. File extensions in domain
14. Suspicious TLDs (.tk, .ml, .ga, .cf)
15. Double slash redirecting

### Machine Learning Models
- **Logistic Regression**: Fast, interpretable baseline (~95% accuracy)
- **Random Forest**: Ensemble classifier for robust predictions (~99% accuracy)

### Risk Levels
- 🔴 **HIGH RISK** (≥75%): Likely phishing
- 🟠 **MEDIUM RISK** (50-75%): Suspicious
- 🟡 **LOW-MEDIUM RISK** (25-50%): Caution advised
- 🟢 **LOW RISK** (<25%): Appears safe

## 📁 Project Structure

```
P_URL_D/
├── app.py                 # Flask web application
├── terminal_app.py        # Terminal interface
├── train_model.py         # Model training script
├── url_features.py        # Feature extraction module
├── requirements.txt       # Python dependencies
├── models/                # Trained ML models
│   ├── lr_model.pkl
│   ├── rf_model.pkl
│   └── feature_extractor.pkl
├── templates/
│   └── index.html         # Web UI
└── static/
    ├── style.css          # Styling
    └── script.js          # Frontend logic
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train Models
```bash
python train_model.py
```
This will generate trained models in the `models/` directory.

### 3. Run Web Application
```bash
python app.py
```
Open `http://localhost:5000` in your browser.

### 4. Run Terminal Application
```bash
python terminal_app.py
```

## 💻 Usage

### Web Interface
1. Navigate to `http://localhost:5000`
2. Enter a URL in the input field
3. Click "Analyze" button
4. View predictions from both models and risk assessment

### Terminal Interface
1. Run `python terminal_app.py`
2. Enter URLs when prompted
3. View detailed analysis with warning signs
4. Type 'exit' to quit

## 📊 Model Performance

| Metric | Logistic Regression | Random Forest |
|--------|-------------------|---------------|
| Accuracy | 95.0% | 99.0% |
| Precision | 95.0% | 99.0% |
| Recall | 95.0% | 99.0% |
| Speed | ~1ms | ~5ms |

## 🔌 API Endpoints

### POST `/api/analyze`
Analyze a URL for phishing indicators.

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
            "probability": 0.15,
            "confidence": "15.0%"
        },
        "random_forest": {
            "prediction": "LEGITIMATE",
            "probability": 0.12,
            "confidence": "12.0%"
        }
    },
    "overall": {
        "prediction": "LEGITIMATE",
        "probability": 0.135,
        "confidence": "13.5%",
        "risk_level": "LOW RISK"
    },
    "warning_signs": []
}
```

### GET `/api/model-info`
Get information about the loaded models.

### GET `/api/health`
Health check endpoint.

## 🛠️ Customization

### Add Custom Features
Edit `url_features.py` and add new feature extraction methods:
```python
def _your_feature(self, url):
    # Your logic here
    return 1 if suspicious else 0
```

### Improve Model Training
Replace synthetic data in `train_model.py` with real datasets:
- PhishtankAPI
- UCIML PhiUSIIL Dataset
- Custom labeled datasets

## ⚠️ Disclaimer

This tool is for educational and security research purposes. It should not be the only security measure for URL validation. Always practice safe browsing habits and use multiple security layers.

## 📝 License

MIT License - Feel free to use and modify for your needs.

## 👨‍💻 Author

P URL D - Phishing URL Detection System

---

**Version**: 1.0.0  
**Last Updated**: December 2024
