import threading
import traceback

from phishing_threat_intel import PhishingDatabaseThreatIntel


class ThreatUpdateScheduler:
    """Background scheduler to sync Phishing.Database feeds and persist new threats.

    Usage:
        scheduler = ThreatUpdateScheduler(interval_seconds=3600)
        scheduler.start()

    The scheduler runs in a daemon thread so it won't block process exit.
    """

    def __init__(self, interval_seconds=3600, intel=None):
        self.interval = max(60, int(interval_seconds))
        self._stop_event = threading.Event()
        self.thread = None
        self.intel = intel or PhishingDatabaseThreatIntel()

    def _sync_once(self):
        try:
            print('[SCHEDULER] Starting feed sync...')
            # Fetch active domains and links (limited to a reasonable number)
            domains = self.intel.fetch_data_source('domains_active', limit=5000)
            links = self.intel.fetch_data_source('links_active', limit=5000)

            new_count = 0

            # Persist domains as threat reports
            for d in domains:
                url = f'https://{d}' if not d.startswith('http') else d
                if getattr(self.intel, 'store', None):
                    report = self.intel.generate_threat_report(url, {
                        'is_known_phishing': True,
                        'threat_type': 'known_phishing_domain',
                        'threat_level': 'critical',
                        'matches': [{'type': 'domain', 'source': 'Phishing.Database (Active Domains)', 'value': d}],
                        'details': {'status': 'ACTIVE', 'confidence': 'VERY_HIGH'}
                    })
                    try:
                        added = self.intel.store.add_threat(report)
                        if added:
                            new_count += 1
                    except Exception:
                        # ignore individual failures
                        pass

            # Persist full links
            for l in links:
                url = l
                if getattr(self.intel, 'store', None):
                    report = self.intel.generate_threat_report(url, {
                        'is_known_phishing': True,
                        'threat_type': 'known_phishing_link',
                        'threat_level': 'critical',
                        'matches': [{'type': 'full_url', 'source': 'Phishing.Database (Active Links)', 'value': l}],
                        'details': {'status': 'ACTIVE', 'confidence': 'VERY_HIGH'}
                    })
                    try:
                        added = self.intel.store.add_threat(report)
                        if added:
                            new_count += 1
                    except Exception:
                        pass

            print(f'[SCHEDULER] Sync complete. New entries stored: {new_count}')

        except Exception as e:
            print('[SCHEDULER] Sync failed:')
            traceback.print_exc()

    def _run(self):
        # Immediate first run
        self._sync_once()
        while not self._stop_event.wait(self.interval):
            self._sync_once()

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print(f'[SCHEDULER] Started background sync every {self.interval} seconds')

    def stop(self):
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)
        print('[SCHEDULER] Stopped')


if __name__ == '__main__':
    # Simple CLI: run one sync then exit
    sched = ThreatUpdateScheduler(interval_seconds=3600)
    sched._sync_once()

