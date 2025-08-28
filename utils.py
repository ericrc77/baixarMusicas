import os
from dotenv import load_dotenv
import json

CONFIG_FILE = "config.json"

def load_environment():
    load_dotenv()

def get_download_dir():
    return os.getenv("DOWNLOAD_DIR", "downloads")

def get_max_concurrency():
    return int(os.getenv("MAX_CONCURRENCY", 3))

def truncate_title(title, length=50):
    return title if len(title) <= length else title[:length] + "..."

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


