"""Check live Phishing.Database for newly observed domains.

This script now integrates with the local threat store and can optionally
trigger a one-shot sync with the live feeds to persist newly observed
threats into `data/new_threats.json` or the SQLite store (`data/threats.db`).
"""

import argparse
import json
from phishing_threat_intel import PhishingDatabaseThreatIntel


def main(sync=False, show_store=False, list_limit=10):
    threat_intel = PhishingDatabaseThreatIntel()

    test_domains = [
        'apple-security-alert.com',
        'paypal-urgent-verify.com',
        'amazon-account-update.com'
    ]

    print('\n[CHECKING LIVE PHISHING.DATABASE]')
    print('=' * 70)
    print('Testing if "newly observed today" domains are in the live database:\n')

    for domain in test_domains:
        url = 'https://' + domain
        result = threat_intel.check_url_against_database(url)

        print(domain)
        print('  Result:', json.dumps(result, indent=2))

        found = result.get('is_known_phishing') if isinstance(result, dict) else bool(result)
        status = 'FOUND IN DATABASE' if found else 'NOT FOUND'
        print('  Status:', status)
        print()

    print('=' * 70)

    if sync:
        # Perform a one-shot feed sync using the scheduler implementation
        try:
            from threat_update_scheduler import ThreatUpdateScheduler
            sched = ThreatUpdateScheduler(interval_seconds=3600, intel=threat_intel)
            print('\n[SYNC] Running one-shot sync...')
            sched._sync_once()
        except Exception as e:
            print('[SYNC ERROR] Could not run sync:', str(e))

    if show_store and getattr(threat_intel, 'store', None):
        print('\n[STORE] Stored threats summary:')
        try:
            count = threat_intel.store.count()
            print(f'  Total stored threats: {count}')
            recent = threat_intel.store.list_threats(limit=list_limit)
            for item in recent:
                url = item.get('url')
                ts = item.get('stored_at') or item.get('report', {}).get('timestamp')
                print(f'   - {ts} | {url}')
        except Exception as e:
            print('[STORE ERROR]', str(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check Phishing.Database and optionally sync/store threats')
    parser.add_argument('--sync', action='store_true', help='Run a one-shot sync and persist new threats')
    parser.add_argument('--show-store', action='store_true', help='Show stored threats and counts')
    parser.add_argument('--limit', type=int, default=10, help='Number of stored threats to list')
    args = parser.parse_args()

    main(sync=args.sync, show_store=args.show_store, list_limit=args.limit)

