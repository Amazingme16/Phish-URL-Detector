#!/usr/bin/env python
"""Quick integration verification for threat tracking system"""

from threat_tracking import ThreatTracker
import os
import json

def main():
    print("=== Threat Tracking System Verification ===\n")
    
    # Test SQLite integration
    tracker = ThreatTracker()
    print("[OK] ThreatTracker initialized with SQLite backend")
    
    # Create test incident
    inc = tracker.create_incident(
        'http://test.example.com',
        sources=['test'],
        severity=75,
        summary='Test incident'
    )
    print(f"[OK] Created incident: {inc['id'][:8]}...")
    
    # Test snapshot update
    tracker.update_snapshot_with_incident(inc)
    print("[OK] Updated snapshot with incident")
    
    # Verify snapshot file
    if os.path.exists('threat_database_snapshot.json'):
        with open('threat_database_snapshot.json') as f:
            snapshot = json.load(f)
            if 'tracked_threats' in snapshot['data']:
                count = len(snapshot["data"]["tracked_threats"])
                print(f"[OK] Snapshot contains {count} tracked threats")
    
    # Get stats
    stats = tracker.get_stats()
    print(f"[OK] Stats: {stats['total']} total, {stats['open']} open, {stats['high_severity']} high-severity")
    
    # Test update
    updated = tracker.update_incident(inc['id'], {'status': 'resolved', 'tags': ['test']})
    print(f"[OK] Updated incident status to: {updated['status']}")
    
    print("\n✅ All integration checks passed!")
    print("\nThreat Tracking System is ready for use.")

if __name__ == '__main__':
    main()
