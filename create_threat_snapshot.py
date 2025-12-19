"""
Threat Database Snapshot Creator
Creates a persistent local copy of threat intelligence data
Survives 24-hour database resets
Run this once to initialize, or periodically to update the snapshot
"""

import json
import os
from datetime import datetime
from phishing_threat_intel import PhishingDatabaseThreatIntel


def create_snapshot():
    """Create a snapshot of threat intelligence data"""
    print("Creating threat database snapshot...")
    print("=" * 60)
    
    intel = PhishingDatabaseThreatIntel()
    
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'version': 'v1.0',
        'data': {
            'domains_active': [],
            'links_active': [],
            'ips_active': [],
            'domains_new_today': [],
            'links_new_today': [],
            'domains_inactive': []
        },
        'status': {}
    }
    
    sources = [
        ('domains_active', 'Active Phishing Domains'),
        ('links_active', 'Active Phishing Links'),
        ('ips_active', 'Active Phishing IPs'),
        ('domains_new_today', 'New Phishing Domains (Today)'),
        ('links_new_today', 'New Phishing Links (Today)'),
        ('domains_inactive', 'Inactive Phishing Domains')
    ]
    
    for source_key, source_name in sources:
        print(f"\nFetching {source_name}...")
        try:
            # Use verify=False to bypass SSL certificate verification
            # In production, proper SSL certificates should be configured
            data = intel.fetch_data_source(source_key, limit=None)
            snapshot['data'][source_key] = list(data)
            snapshot['status'][source_key] = {
                'count': len(data),
                'status': 'SUCCESS'
            }
            print(f"  [OK] Fetched {len(data)} entries")
        except Exception as e:
            snapshot['status'][source_key] = {
                'count': 0,
                'status': 'FAILED',
                'error': str(e)
            }
            print(f"  [FAIL] Failed: {str(e)}")
    
    # Save snapshot
    snapshot_file = 'threat_database_snapshot.json'
    try:
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        total_entries = sum(len(v) for k, v in snapshot['data'].items())
        print(f"\n{'=' * 60}")
        print(f"[OK] Snapshot created successfully: {snapshot_file}")
        print(f"Total threat entries: {total_entries}")
        print(f"Timestamp: {snapshot['timestamp']}")
        
        return True
    except Exception as e:
        print(f"\n[FAIL] Error saving snapshot: {str(e)}")
        return False


if __name__ == '__main__':
    create_snapshot()
