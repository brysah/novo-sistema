import os
import json
from threading import Lock
from typing import List

NEWSLETTERS_FILE = "newsletters.json"

class NewsletterManager:
    def __init__(self, file_path: str = NEWSLETTERS_FILE):
        self.file_path = file_path
        self._lock = Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({"newsletters": []}, f, indent=2, ensure_ascii=False)

    def get_all(self) -> List[str]:
        with self._lock:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("newsletters", [])

    def add(self, url: str):
        with self._lock:
            newsletters = self.get_all()
            if url not in newsletters:
                newsletters.append(url)
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump({"newsletters": newsletters}, f, indent=2, ensure_ascii=False)

    def remove(self, url: str):
        with self._lock:
            newsletters = self.get_all()
            if url in newsletters:
                newsletters.remove(url)
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump({"newsletters": newsletters}, f, indent=2, ensure_ascii=False)

newsletter_manager = NewsletterManager()
