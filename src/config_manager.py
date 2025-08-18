import json
import os
from typing import Any

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')

class ConfigManager:
    def __init__(self):
        self.config = self.load()

    def load(self) -> dict:
        if not os.path.exists(CONFIG_PATH):
            return {"download_dir": "downloads", "max_concurrent_downloads": 3}
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self):
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value
        self.save()
