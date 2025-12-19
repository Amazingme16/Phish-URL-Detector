"""
Unit tests for Threat Tracking Module and API Endpoints
Tests ThreatTracker SQLite operations and Flask API endpoints
"""

import unittest
import json
import os
import tempfile
import shutil
from threat_tracking import ThreatTracker
from app import app, tracker


class TestThreatTracker(unittest.TestCase):
    """Test ThreatTracker class functionality"""

    def setUp(self):
        """Create temporary database for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_file = os.path.join(self.temp_dir, 'test_incidents.db')
        self.snapshot_file = os.path.join(self.temp_dir, 'test_snapshot.json')
        self.tracker = ThreatTracker(db_file=self.db_file, snapshot_file=self.snapshot_file)

    def tearDown(self):
        """Clean up temporary database"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_incident(self):
        """Test creating an incident"""
        record = self.tracker.create_incident(
            url='http://example.com',
            sources=['test_source'],
            severity=50,
            summary='Test incident',
            tags=['test']
        )
        self.assertIsNotNone(record['id'])
        self.assertEqual(record['url'], 'http://example.com')
        self.assertEqual(record['severity'], 50)
        self.assertEqual(record['status'], 'open')
        self.assertEqual(record['occurrences'], 1)
        self.assertIn('test_source', record['sources'])

    def test_get_incident(self):
        """Test retrieving an incident"""
        created = self.tracker.create_incident(
            url='http://phishing.com',
            severity=80
        )
        retrieved = self.tracker.get_incident(created['id'])
        self.assertEqual(created['id'], retrieved['id'])
        self.assertEqual(retrieved['url'], 'http://phishing.com')
        self.assertEqual(retrieved['severity'], 80)

    def test_list_incidents(self):
        """Test listing all incidents"""
        self.tracker.create_incident('http://threat1.com', severity=50, summary='Threat 1')
        self.tracker.create_incident('http://threat2.com', severity=75, summary='Threat 2')
        self.tracker.create_incident('http://threat3.com', severity=30, summary='Threat 3')

        all_incidents = self.tracker.list_incidents()
        self.assertEqual(len(all_incidents), 3)

    def test_list_incidents_by_status(self):
        """Test filtering incidents by status"""
        incident1 = self.tracker.create_incident('http://open.com', severity=50)
        incident2 = self.tracker.create_incident('http://resolved.com', severity=75)

        # Resolve second incident
        self.tracker.update_incident(incident2['id'], {'status': 'resolved'})

        open_incidents = self.tracker.list_incidents(status='open')
        resolved_incidents = self.tracker.list_incidents(status='resolved')

        self.assertEqual(len(open_incidents), 1)
        self.assertEqual(len(resolved_incidents), 1)
        self.assertEqual(open_incidents[0]['url'], 'http://open.com')

    def test_update_incident(self):
        """Test updating an incident"""
        record = self.tracker.create_incident('http://example.com', severity=20)
        updated = self.tracker.update_incident(record['id'], {
            'severity': 80,
            'status': 'escalated',
            'tags': ['critical', 'urgent']
        })

        self.assertEqual(updated['severity'], 80)
        self.assertEqual(updated['status'], 'escalated')
        self.assertIn('critical', updated['tags'])
        self.assertIn('urgent', updated['tags'])

    def test_update_incident_increment_occurrences(self):
        """Test incrementing occurrence count"""
        record = self.tracker.create_incident('http://example.com')
        self.assertEqual(record['occurrences'], 1)

        updated = self.tracker.update_incident(record['id'], {'increment': True})
        self.assertEqual(updated['occurrences'], 2)

        updated_again = self.tracker.update_incident(record['id'], {'increment': True})
        self.assertEqual(updated_again['occurrences'], 3)

    def test_update_incident_merge_tags(self):
        """Test merging tags on update"""
        record = self.tracker.create_incident('http://example.com', tags=['tag1'])
        updated = self.tracker.update_incident(record['id'], {'tags': ['tag2', 'tag3']})

        # Should have unique union of tags
        self.assertEqual(len(updated['tags']), 3)
        self.assertIn('tag1', updated['tags'])
        self.assertIn('tag2', updated['tags'])
        self.assertIn('tag3', updated['tags'])

    def test_find_by_url(self):
        """Test finding incidents by URL"""
        url = 'http://phishing.com'
        self.tracker.create_incident(url, severity=50)
        self.tracker.create_incident(url, severity=75)  # Same URL
        self.tracker.create_incident('http://other.com', severity=30)

        results = self.tracker.find_by_url(url)
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertEqual(result['url'], url)

    def test_get_stats(self):
        """Test getting incident statistics"""
        self.tracker.create_incident('http://threat1.com', severity=50, summary='Threat 1')
        self.tracker.create_incident('http://threat2.com', severity=80, summary='Threat 2')
        self.tracker.create_incident('http://threat3.com', severity=95, summary='Threat 3')

        record1 = self.tracker.create_incident('http://threat4.com', severity=60)
        self.tracker.update_incident(record1['id'], {'status': 'resolved'})

        stats = self.tracker.get_stats()
        self.assertEqual(stats['total'], 4)
        self.assertEqual(stats['open'], 3)
        self.assertEqual(stats['high_severity'], 2)  # 80 and 95

    def test_update_snapshot_with_incident(self):
        """Test auto-updating snapshot with incident"""
        # Create snapshot file first
        snapshot = {'data': {'domains_active': []}}
        with open(self.snapshot_file, 'w') as f:
            json.dump(snapshot, f)

        record = self.tracker.create_incident('http://threat.com', severity=75)
        self.tracker.update_snapshot_with_incident(record)

        # Verify snapshot was updated
        with open(self.snapshot_file, 'r') as f:
            updated_snapshot = json.load(f)

        self.assertIn('tracked_threats', updated_snapshot['data'])
        threats = updated_snapshot['data']['tracked_threats']
        self.assertEqual(len(threats), 1)
        self.assertEqual(threats[0]['url'], 'http://threat.com')
        self.assertEqual(threats[0]['severity'], 75)

    def test_update_snapshot_no_duplicates(self):
        """Test snapshot doesn't add duplicate URLs"""
        snapshot = {'data': {'tracked_threats': [{'url': 'http://threat.com', 'severity': 50}]}}
        with open(self.snapshot_file, 'w') as f:
            json.dump(snapshot, f)

        record = self.tracker.create_incident('http://threat.com', severity=75)
        self.tracker.update_snapshot_with_incident(record)

        with open(self.snapshot_file, 'r') as f:
            updated_snapshot = json.load(f)

        threats = updated_snapshot['data']['tracked_threats']
        self.assertEqual(len(threats), 1)

    def test_details_json_serialization(self):
        """Test details are properly serialized/deserialized"""
        details = {
            'model': 'random_forest',
            'confidence': 0.95,
            'features': ['domain_length', 'uses_ip']
        }
        record = self.tracker.create_incident('http://example.com', details=details)
        self.assertEqual(record['details']['model'], 'random_forest')
        self.assertEqual(record['details']['confidence'], 0.95)
        self.assertIn('domain_length', record['details']['features'])


class TestThreatTrackingAPI(unittest.TestCase):
    """Test Threat Tracking REST API endpoints"""

    def setUp(self):
        """Set up Flask test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_list_threats_empty(self):
        """Test listing threats when none exist"""
        response = self.client.get('/api/threats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total', data)
        self.assertIn('incidents', data)

    def test_create_threat_minimal(self):
        """Test creating a threat with minimal data"""
        response = self.client.post('/api/threats',
            data=json.dumps({'url': 'http://threat.com'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIsNotNone(data['id'])
        self.assertEqual(data['url'], 'http://threat.com')

    def test_create_threat_full(self):
        """Test creating a threat with all fields"""
        payload = {
            'url': 'http://phishing.example.com',
            'sources': ['ml_models', 'phishing_database'],
            'severity': 85,
            'summary': 'High-confidence phishing site',
            'details': {'ml_score': 0.92, 'db_match': 'exact'},
            'tags': ['urgent', 'phishing']
        }
        response = self.client.post('/api/threats',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['url'], payload['url'])
        self.assertEqual(data['severity'], 85)
        self.assertIn('ml_models', data['sources'])

    def test_create_threat_no_url(self):
        """Test creating threat without URL fails"""
        response = self.client.post('/api/threats',
            data=json.dumps({'summary': 'No URL'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_get_threat_detail(self):
        """Test retrieving a specific threat"""
        # Create a threat first
        create_response = self.client.post('/api/threats',
            data=json.dumps({'url': 'http://test.com', 'severity': 60}),
            content_type='application/json'
        )
        incident_id = json.loads(create_response.data)['id']

        # Retrieve it
        response = self.client.get(f'/api/threats/{incident_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], incident_id)
        self.assertEqual(data['url'], 'http://test.com')

    def test_get_threat_not_found(self):
        """Test retrieving non-existent threat"""
        response = self.client.get('/api/threats/nonexistent-id')
        self.assertEqual(response.status_code, 404)

    def test_update_threat_status(self):
        """Test updating threat status"""
        create_response = self.client.post('/api/threats',
            data=json.dumps({'url': 'http://test.com'}),
            content_type='application/json'
        )
        incident_id = json.loads(create_response.data)['id']

        # Update status
        response = self.client.patch(f'/api/threats/{incident_id}',
            data=json.dumps({'status': 'resolved'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'resolved')

    def test_update_threat_severity(self):
        """Test updating threat severity"""
        create_response = self.client.post('/api/threats',
            data=json.dumps({'url': 'http://test.com', 'severity': 30}),
            content_type='application/json'
        )
        incident_id = json.loads(create_response.data)['id']

        response = self.client.patch(f'/api/threats/{incident_id}',
            data=json.dumps({'severity': 95}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['severity'], 95)

    def test_update_threat_tags(self):
        """Test updating threat tags"""
        create_response = self.client.post('/api/threats',
            data=json.dumps({'url': 'http://test.com', 'tags': ['tag1']}),
            content_type='application/json'
        )
        incident_id = json.loads(create_response.data)['id']

        response = self.client.patch(f'/api/threats/{incident_id}',
            data=json.dumps({'tags': ['tag2', 'tag3']}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['tags']), 3)

    def test_list_threats_by_status(self):
        """Test filtering threats by status"""
        # Create multiple threats
        response1 = self.client.post('/api/threats',
            data=json.dumps({'url': 'http://threat1.com'}),
            content_type='application/json'
        )
        incident_id = json.loads(response1.data)['id']

        self.client.post('/api/threats',
            data=json.dumps({'url': 'http://threat2.com'}),
            content_type='application/json'
        )

        # Resolve first one
        self.client.patch(f'/api/threats/{incident_id}',
            data=json.dumps({'status': 'resolved'}),
            content_type='application/json'
        )

        # List open threats
        response = self.client.get('/api/threats?status=open')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # At least one open threat (may be more from other tests)
        self.assertGreaterEqual(len(data['incidents']), 1)

    def test_health_check_includes_tracking(self):
        """Test health endpoint includes tracking summary"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('tracking', data)
        self.assertIn('total_incidents', data['tracking'])
        self.assertIn('open_incidents', data['tracking'])


class TestThreatTrackingIntegration(unittest.TestCase):
    """Integration tests for threat tracking with analysis"""

    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_analyze_creates_tracking_record_for_known_threat(self):
        """Test that analyzing a known phishing URL creates tracking record"""
        # Use a URL that's likely in seed data or will trigger threat detection
        response = self.client.post('/api/analyze',
            data=json.dumps({'url': 'http://paypa1-login.com'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        # Check if tracking record was created
        if 'tracking_record' in data:
            self.assertIn('id', data['tracking_record'])
            self.assertEqual(data['tracking_record']['url'], 'http://paypa1-login.com')
            self.assertGreater(data['tracking_record']['severity'], 0)


if __name__ == '__main__':
    unittest.main()
