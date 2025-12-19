import os
import json
import hashlib
from datetime import datetime


class ThreatStore:
    """Simple JSON-backed store for newly detected threats.

    Stores reports as a list of objects in `data/new_threats.json` by default.
    Provides deduplication based on URL SHA256.
    """

    def __init__(self, path='data/new_threats.json'):
        self.path = path
        self._ensure_store()
        self._load()

    def _ensure_store(self):
        dir_path = os.path.dirname(self.path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _load(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                self._items = json.load(f)
        except Exception:
            self._items = []

    def _save(self):
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self._items, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise

    def _id_for_url(self, url):
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def exists(self, url):
        _id = self._id_for_url(url)
        for item in self._items:
            if item.get('id') == _id:
                return True
        return False

    def add_threat(self, report):
        """Add a threat report if it doesn't already exist.

        Returns True if added, False if already present.
        """
        url = report.get('url') or report.get('domain') or ''
        if not url:
            return False

        _id = self._id_for_url(url)
        if self.exists(url):
            return False

        stored = {
            'id': _id,
            'url': url,
            'stored_at': datetime.utcnow().isoformat() + 'Z',
            'report': report
        }
        self._items.append(stored)
        self._save()
        return True

    def list_threats(self, limit=1000):
        return list(self._items[-limit:])

    def count(self):
        return len(self._items)
