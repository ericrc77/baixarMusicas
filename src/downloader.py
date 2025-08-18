
import os
import re
import time
import logging
from typing import List, Callable
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
import requests
from src.config_manager import ConfigManager

config = ConfigManager()
CHUNK_SIZE = int(config.get('chunk_size_mb', 1)) * 1024 * 1024
DEFAULT_RETRIES = int(config.get('retries', 3))
DEFAULT_TIMEOUT = int(config.get('timeout', 15))

class DownloadSignals(QObject):
    progress = pyqtSignal(int, int)  # index, percent
    finished = pyqtSignal(int, str)  # index, status
    error = pyqtSignal(int, str)     # index, error message


class DownloadTask(QRunnable):
    def __init__(self, url: str, dest: str, index: int, signals: DownloadSignals, retries: int = None, timeout: int = None):
        super().__init__()
        self.url = url
        self.dest = dest
        self.index = index
        self.signals = signals
        self.retries = retries if retries is not None else DEFAULT_RETRIES
        self.timeout = timeout if timeout is not None else DEFAULT_TIMEOUT

    def run(self):
        attempt = 0
        while attempt <= self.retries:
            try:
                with requests.get(self.url, stream=True, timeout=self.timeout) as r:
                    r.raise_for_status()
                    total = int(r.headers.get('content-length', 0))
                    with open(self.dest, 'wb') as f:
                        downloaded = 0
                        for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                percent = int(downloaded * 100 / total) if total else 0
                                self.signals.progress.emit(self.index, percent)
                    self.signals.finished.emit(self.index, 'Concluído')
                    return
            except Exception as e:
                attempt += 1
                if attempt > self.retries:
                    self.signals.error.emit(self.index, f"Erro: {str(e)}")
                    return
                time.sleep(2 ** attempt)  # Exponential backoff


def sanitize_filename(filename: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', '_', filename)
