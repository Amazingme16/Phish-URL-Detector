"""
Flask Web Application for Phishing URL Detection
Provides web interface and API endpoints
"""

from flask import Flask, render_template, request, jsonify
import pickle
import os
from url_features import URLFeatureExtractor
from url_dataset_loader import URLDatasetLoader
from advanced_features import AdvancedURLAnalyzer
from link_threats_detector import LinkThreatsDetector
from phishing_threat_intel import PhishingDatabaseThreatIntel
from ai_code_agents import CodeManagementOrchestrator
from threat_tracking import ThreatTracker

app = Flask(__name__)

# Load models
try:
    with open('models/lr_model.pkl', 'rb') as f:
        lr_model = pickle.load(f)
    with open('models/rf_model.pkl', 'rb') as f:
        rf_model = pickle.load(f)
    with open('models/feature_extractor.pkl', 'rb') as f:
        feature_extractor = pickle.load(f)
except FileNotFoundError:
    print("Models not found! Please run train_model.py first.")
    feature_extractor = URLFeatureExtractor()
    lr_model = None
    rf_model = None

# Initialize advanced analyzer and link threats detector
advanced_analyzer = AdvancedURLAnalyzer()
link_threats_detector = LinkThreatsDetector()
threat_intel = PhishingDatabaseThreatIntel()
orchestrator = CodeManagementOrchestrator('.')

# Threat tracking
tracker = ThreatTracker()

# Initialize seed dataset loader
seed_loader = URLDatasetLoader('data/seed_urls.csv')
seed_dataset_loaded = seed_loader.load_dataset()
seed_dataset_info = seed_loader.get_dataset_info() if seed_dataset_loaded else {}

def get_risk_level(probability):
    """Classify risk level based on probability"""
    if probability >= 0.75:
        return "HIGH RISK"
    elif probability >= 0.50:
        return "MEDIUM RISK"
    elif probability >= 0.25:
        return "LOW-MEDIUM RISK"
    else:
        return "LOW RISK"

def get_risk_color(probability):
    """Get color code for risk level"""
    if probability >= 0.75:
        return "#d32f2f"  # Red
    elif probability >= 0.50:
        return "#f57c00"  # Orange
    elif probability >= 0.25:
        return "#fbc02d"  # Yellow
    else:
        return "#388e3c"  # Green

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_url():
    """
    API endpoint to analyze a URL
    POST data: {'url': 'https://example.com'}
    Returns: JSON with predictions and risk analysis
    """
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'No URL provided', 'status': 'error'}), 400
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # Extract features for ML prediction
        features = feature_extractor.extract_features(url)
        
        # Get predictions
        results = {
            'url': url,
            'status': 'success'
        }
        
        if lr_model and rf_model:
            # Logistic Regression prediction
            lr_pred = lr_model.predict([features])[0]
            lr_prob = lr_model.predict_proba([features])[0][1]
            
            # Random Forest prediction
            rf_pred = rf_model.predict([features])[0]
            rf_prob = rf_model.predict_proba([features])[0][1]
            
            # Average probability
            avg_prob = (lr_prob + rf_prob) / 2
            
            results['models'] = {
                'logistic_regression': {
                    'prediction': 'PHISHING' if lr_pred == 1 else 'LEGITIMATE',
                    'probability': float(lr_prob),
                    'confidence': f"{lr_prob*100:.1f}%"
                },
                'random_forest': {
                    'prediction': 'PHISHING' if rf_pred == 1 else 'LEGITIMATE',
                    'probability': float(rf_prob),
                    'confidence': f"{rf_prob*100:.1f}%"
                }
            }
            
            results['overall'] = {
                'prediction': 'PHISHING' if avg_prob >= 0.5 else 'LEGITIMATE',
                'probability': float(avg_prob),
                'confidence': f"{avg_prob*100:.1f}%",
                'risk_level': get_risk_level(avg_prob),
                'risk_color': get_risk_color(avg_prob)
            }
            
            # Feature analysis
            feature_names = feature_extractor.get_feature_names()
            warning_signs = []
            for i, (feature_name, feature_value) in enumerate(zip(feature_names, features)):
                if feature_value == 1:
                    warning_signs.append(feature_name.replace('_', ' ').title())
            
            results['warning_signs'] = warning_signs
        else:
            results['status'] = 'error'
            results['error'] = 'Models not loaded. Please train the model first.'
            return jsonify(results), 500
        
        # Run advanced checks
        try:
            advanced_results = advanced_analyzer.get_all_checks(url)
            results['advanced_analysis'] = advanced_results
        except Exception as e:
            # Advanced analysis failed, but continue with ML results
            print(f"Advanced analysis error: {str(e)}")
        
        # Run link threats detection
        try:
            link_threats = link_threats_detector.detect_all_threats(url)
            results['link_threats'] = link_threats
        except Exception as e:
            # Link threats detection failed, but continue with other results
            print(f"Link threats detection error: {str(e)}")
        
        # Run threat intelligence check (Phishing.Database)
        try:
            threat_intel_result = threat_intel.check_url_against_database(url)
            threat_intel_report = threat_intel.generate_threat_report(url, threat_intel_result)
            results['threat_intelligence'] = threat_intel_report
        except Exception as e:
            # Threat intelligence failed, but continue with other results
            print(f"Threat intelligence error: {str(e)}")

        # Create/update threat tracking record if a threat is detected or score high
        try:
            created_record = None
            severity = 0
            sources = []

            if 'threat_intelligence' in results and results['threat_intelligence'].get('threat_found'):
                sources.append('phishing_database')
                severity = max(severity, results['threat_intelligence'].get('threat_severity', 0))

            if 'link_threats' in results and isinstance(results['link_threats'].get('threat_score'), (int, float)):
                lt_score = int(results['link_threats'].get('threat_score', 0))
                if lt_score >= 25:
                    sources.append('link_threats_detector')
                severity = max(severity, lt_score)

            # Consider ML overall prediction too
            if 'overall' in results and results['overall'].get('prediction') == 'PHISHING':
                sources.append('ml_models')
                severity = max(severity, int(results['overall'].get('probability', 0) * 100))

            if sources and severity > 0:
                summary = f"Detected potential threat for {url} (sources: {', '.join(sources)})"
                details = {
                    'models': results.get('models'),
                    'link_threats': results.get('link_threats'),
                    'threat_intelligence': results.get('threat_intelligence')
                }
                created_record = tracker.create_incident(url, sources=sources, severity=severity, summary=summary, details=details)
                # Auto-update snapshot with the tracked threat
                tracker.update_snapshot_with_incident(created_record)
                results['tracking_record'] = created_record
        except Exception as e:
            print(f"Threat tracking error: {str(e)}")
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get information about the models"""
    return jsonify({
        'models_loaded': lr_model is not None and rf_model is not None,
        'features_count': 15,
        'feature_names': feature_extractor.get_feature_names(),
        'algorithms': ['Logistic Regression', 'Random Forest']
    })

@app.route('/api/seed-dataset', methods=['GET'])
def get_seed_dataset():
    """Get seed dataset information and statistics"""
    if seed_dataset_loaded:
        validation = seed_loader.validate_urls()
        return jsonify({
            'status': 'loaded',
            'info': seed_dataset_info,
            'validation': {
                'total': validation['total'],
                'valid': validation['valid'],
                'invalid': validation['invalid']
            },
            'phishing_samples': seed_loader.get_phishing_urls()[:3],
            'legitimate_samples': seed_loader.get_legitimate_urls()[:3]
        })
    else:
        return jsonify({
            'status': 'not_loaded',
            'message': 'Seed dataset not available at data/seed_urls.csv'
        }), 404


@app.route('/api/threats', methods=['GET'])
def list_threats():
    """List all tracked threat incidents"""
    status = request.args.get('status')
    incidents = tracker.list_incidents(status=status)
    return jsonify({'total': len(incidents), 'incidents': incidents})


@app.route('/api/threats', methods=['POST'])
def create_threat():
    """Create a manual threat incident"""
    data = request.get_json() or {}
    url = data.get('url')
    if not url:
        return jsonify({'error': 'url is required'}), 400

    record = tracker.create_incident(
        url,
        sources=data.get('sources'),
        severity=data.get('severity', 0),
        summary=data.get('summary'),
        details=data.get('details'),
        tags=data.get('tags')
    )
    # Auto-update snapshot
    tracker.update_snapshot_with_incident(record)
    return jsonify(record), 201


@app.route('/api/threats/<incident_id>', methods=['GET', 'PATCH'])
def threat_detail(incident_id):
    if request.method == 'GET':
        record = tracker.get_incident(incident_id)
        if not record:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(record)

    # PATCH: update
    data = request.get_json() or {}
    updated = tracker.update_incident(incident_id, data)
    if not updated:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(updated)

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint with threat database and seed dataset status"""
    health_status = {
        'status': 'healthy',
        'models_ready': lr_model is not None and rf_model is not None,
        'seed_dataset_loaded': seed_dataset_loaded,
        'threat_database': {
            'snapshot_available': bool(threat_intel.snapshot_data),
            'cache_available': bool(threat_intel.local_cache),
            'snapshot_entries': sum(len(v) for v in threat_intel.snapshot_data.values()),
            'cache_entries': sum(len(v) for v in threat_intel.local_cache.values())
        }
    }
    
    if seed_dataset_loaded:
        health_status['seed_dataset'] = seed_dataset_info
    
    # Check if no data is available at all
    if not threat_intel.snapshot_data and not threat_intel.local_cache:
        health_status['warning'] = 'No threat database available. Run create_threat_snapshot.py to initialize.'

    # Threat tracking summary
    try:
        tracking_stats = tracker.get_stats()
        health_status['tracking'] = {
            'total_incidents': tracking_stats['total'],
            'open_incidents': tracking_stats['open'],
            'high_severity_incidents': tracking_stats['high_severity']
        }
    except Exception:
        health_status['tracking'] = {'total_incidents': 0, 'open_incidents': 0}
    
    return jsonify(health_status)


if __name__ == '__main__':
    # Only run in development - production uses Gunicorn
    app.run(debug=True, host='0.0.0.0', port=5000)
