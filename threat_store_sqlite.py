import sqlite3
import os
import json
from datetime import datetime


class ThreatStoreSQLite:
    """SQLite-backed store for newly detected threats.

    Creates a local `data/threats.db` SQLite database and provides simple
    add/list/exists/count operations.
    """

    def __init__(self, path='data/threats.db'):
        self.path = path
        dir_path = os.path.dirname(self.path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self._ensure_schema()

    def _ensure_schema(self):
        cur = self.conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS threats (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            stored_at TEXT NOT NULL,
            report_json TEXT
        )
        ''')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_url ON threats(url)')
        self.conn.commit()

    def _id_for_url(self, url):
        import hashlib
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def exists(self, url):
        _id = self._id_for_url(url)
        cur = self.conn.cursor()
        cur.execute('SELECT 1 FROM threats WHERE id=? LIMIT 1', (_id,))
        return cur.fetchone() is not None

    def add_threat(self, report):
        url = report.get('url') or report.get('domain') or ''
        if not url:
            return False
        _id = self._id_for_url(url)
        if self.exists(url):
            return False
        cur = self.conn.cursor()
        cur.execute('INSERT INTO threats (id, url, stored_at, report_json) VALUES (?, ?, ?, ?)', (
            _id,
            url,
            datetime.utcnow().isoformat() + 'Z',
            json.dumps(report)
        ))
        self.conn.commit()
        return True

    def list_threats(self, limit=1000):
        cur = self.conn.cursor()
        cur.execute('SELECT id, url, stored_at, report_json FROM threats ORDER BY stored_at DESC LIMIT ?', (limit,))
        rows = cur.fetchall()
        results = []
        for r in rows:
            results.append({'id': r[0], 'url': r[1], 'stored_at': r[2], 'report': json.loads(r[3]) if r[3] else None})
        return results

    def count(self):
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(*) FROM threats')
        return cur.fetchone()[0]

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass
