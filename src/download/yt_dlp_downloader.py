"""
Módulo para baixar músicas/vídeos usando yt-dlp.
"""
from typing import List
import os

class DownloadItem:
    def __init__(self, title: str, url: str, dest: str, formato: str = 'mp4'):
        self.title = title
        self.url = url
        self.dest = dest
        self.formato = formato


import yt_dlp

def baixar_musicas(lista: List[DownloadItem], progresso_callback=None, log_callback=None):
    """Baixa músicas/vídeos usando yt-dlp."""
    for idx, item in enumerate(lista):
        if log_callback:
            log_callback(f"Iniciando download: {item.title}")
        ydl_opts = {
            'outtmpl': os.path.join(item.dest, f"%(title)s.%(ext)s"),
            'format': 'bestaudio/best' if item.formato == 'mp3' else 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            'noplaylist': True,
            'quiet': True,
            'progress_hooks': [
                lambda d: progresso_callback(idx, d) if progresso_callback else None
            ],
        }
        if item.formato == 'mp3':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([item.url])
            if log_callback:
                log_callback(f"Concluído: {item.title}")
        except Exception as e:
            if log_callback:
                log_callback(f"Erro ao baixar {item.title}: {e}")
