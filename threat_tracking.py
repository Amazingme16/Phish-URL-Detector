import json
import os
import uuid
import sqlite3
from datetime import datetime, timezone
from contextlib import contextmanager


class ThreatTracker:
    """SQLite-backed threat tracking for detected incidents"""

    def __init__(self, db_file='threat_tracking.db', snapshot_file='threat_database_snapshot.json'):
        self.db_file = db_file
        self.snapshot_file = snapshot_file
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database schema"""
        with self._get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    sources TEXT NOT NULL,
                    severity INTEGER DEFAULT 0,
                    summary TEXT,
                    details TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    status TEXT DEFAULT 'open',
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    occurrences INTEGER DEFAULT 1
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_url ON incidents(url)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_status ON incidents(status)')
            conn.commit()

    @contextmanager
    def _get_conn(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _now(self):
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    def _dict_from_row(self, row):
        """Convert sqlite3.Row to dict, parsing JSON fields"""
        if row is None:
            return None
        d = dict(row)
        d['sources'] = json.loads(d['sources']) if d['sources'] else []
        d['details'] = json.loads(d['details']) if d['details'] else {}
        d['tags'] = json.loads(d['tags']) if d['tags'] else []
        return d

    def create_incident(self, url, sources=None, severity=0, summary=None, details=None, tags=None):
        iid = str(uuid.uuid4())
        now = self._now()
        sources_json = json.dumps(sources or [])
        details_json = json.dumps(details or {})
        tags_json = json.dumps(tags or [])

        with self._get_conn() as conn:
            conn.execute('''
                INSERT INTO incidents (id, url, sources, severity, summary, details, tags, status, first_seen, last_seen, occurrences)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (iid, url, sources_json, int(severity or 0), summary or '', details_json, tags_json, 'open', now, now, 1))
            conn.commit()

        return self.get_incident(iid)

    def get_incident(self, iid):
        with self._get_conn() as conn:
            row = conn.execute('SELECT * FROM incidents WHERE id = ?', (iid,)).fetchone()
            return self._dict_from_row(row)

    def list_incidents(self, status=None):
        with self._get_conn() as conn:
            if status:
                rows = conn.execute('SELECT * FROM incidents WHERE status = ? ORDER BY last_seen DESC', (status,)).fetchall()
            else:
                rows = conn.execute('SELECT * FROM incidents ORDER BY last_seen DESC').fetchall()
            return [self._dict_from_row(row) for row in rows]

    def update_incident(self, iid, updates: dict):
        record = self.get_incident(iid)
        if not record:
            return None

        # Merge updates
        for k, v in updates.items():
            if k in ['severity']:
                record[k] = int(v)
            elif k in ['tags', 'sources'] and isinstance(v, list):
                # extend lists
                record[k] = list({*record.get(k, []), *v})
            elif k == 'status':
                record[k] = v
            elif k == 'details' and isinstance(v, dict):
                record[k].update(v)
            else:
                record[k] = v

        record['last_seen'] = self._now()
        if updates.get('increment', False):
            record['occurrences'] = record.get('occurrences', 1) + 1

        # Write back
        with self._get_conn() as conn:
            conn.execute('''
                UPDATE incidents SET sources = ?, severity = ?, summary = ?, details = ?, tags = ?, status = ?, last_seen = ?, occurrences = ?
                WHERE id = ?
            ''', (
                json.dumps(record['sources']),
                record['severity'],
                record['summary'],
                json.dumps(record['details']),
                json.dumps(record['tags']),
                record['status'],
                record['last_seen'],
                record['occurrences'],
                iid
            ))
            conn.commit()

        return record

    def find_by_url(self, url):
        with self._get_conn() as conn:
            rows = conn.execute('SELECT * FROM incidents WHERE url = ?', (url,)).fetchall()
            return [self._dict_from_row(row) for row in rows]

    def update_snapshot_with_incident(self, incident):
        """Auto-update threat_database_snapshot.json when incident created/updated"""
        try:
            snapshot_data = {}
            if os.path.exists(self.snapshot_file):
                with open(self.snapshot_file, 'r', encoding='utf-8') as f:
                    snapshot_data = json.load(f)

            if 'data' not in snapshot_data:
                snapshot_data['data'] = {}

            # Add incident URL to a new 'tracked_threats' section
            if 'tracked_threats' not in snapshot_data['data']:
                snapshot_data['data']['tracked_threats'] = []

            threat_entry = {
                'url': incident['url'],
                'severity': incident['severity'],
                'sources': incident['sources'],
                'status': incident['status'],
                'first_seen': incident['first_seen']
            }

            # Check for duplicates
            existing = [t for t in snapshot_data['data']['tracked_threats'] if t['url'] == incident['url']]
            if not existing:
                snapshot_data['data']['tracked_threats'].append(threat_entry)

            # Write atomically
            tmp = f"{self.snapshot_file}.tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self.snapshot_file)
        except Exception as e:
            print(f"[WARN] Snapshot update failed: {str(e)}")

    def get_stats(self):
        """Get incident statistics"""
        with self._get_conn() as conn:
            total = conn.execute('SELECT COUNT(*) FROM incidents').fetchone()[0]
            open_count = conn.execute("SELECT COUNT(*) FROM incidents WHERE status = 'open'").fetchone()[0]
            high_severity = conn.execute('SELECT COUNT(*) FROM incidents WHERE severity >= 75').fetchone()[0]
        return {
            'total': total,
            'open': open_count,
            'high_severity': high_severity
        }


__all__ = ['ThreatTracker']
