import yt_dlp
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json

from utils import get_download_dir

HISTORY_FILE = os.path.join(get_download_dir(), "history.json")

def save_history(video_info):
    """Salva as informações do vídeo baixado no histórico."""
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    history.append(video_info)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def download_audio(url, outdir, log_cb=None, progress_hook=None):
    """Baixa o áudio de um vídeo do YouTube."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(outdir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [progress_hook] if progress_hook else [],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            save_history({
                "title": info.get("title", "N/A"),
                "url": url,
                "format": "mp3",
                "download_date": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        if log_cb: log_cb(f"Download de áudio concluído: {info.get('title', url)}")
    except yt_dlp.utils.DownloadError as e:
        if log_cb: log_cb(f"Erro de download de áudio de {url}: {e}")
    except Exception as e:
        if log_cb: log_cb(f"Erro inesperado ao baixar áudio de {url}: {e}")

def download_video(url, outdir, quality, log_cb=None, progress_hook=None):
    """Baixa o vídeo de um vídeo do YouTube com a qualidade especificada."""
    format_string = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]" if quality else "bestvideo+bestaudio/best"
    ydl_opts = {
        'format': format_string,
        'outtmpl': os.path.join(outdir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook] if progress_hook else [],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            save_history({
                "title": info.get("title", "N/A"),
                "url": url,
                "format": f"mp4 ({quality}p)",
                "download_date": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        if log_cb: log_cb(f"Download de vídeo concluído: {info.get('title', url)}")
    except yt_dlp.utils.DownloadError as e:
        if log_cb: log_cb(f"Erro de download de vídeo de {url}: {e}")
    except Exception as e:
        if log_cb: log_cb(f"Erro inesperado ao baixar vídeo de {url}: {e}")

def download_many(urls, concurrency, format, outdir, progress_cb=None, log_cb=None, quality=None):
    """Gerencia o download de múltiplos vídeos/áudios em paralelo."""
    download_func = download_audio if format == 'mp3' else (lambda u, o, l, ph: download_video(u, o, quality, l, ph))
    
    total_downloads = len(urls)
    completed_downloads = 0

    def _progress_hook(d):
        nonlocal completed_downloads
        if d['status'] == 'finished':
            completed_downloads += 1
            if progress_cb: progress_cb(completed_downloads, total_downloads)
        if d['status'] == 'downloading':
            if log_cb and '_eta_str' in d:
                log_cb(f"Progresso: {d['_percent_str']} de {d['total_bytes_str']} ETA: {d['_eta_str']}")

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for url in urls:
            futures.append(executor.submit(download_func, url, outdir, log_cb, _progress_hook))
        
        for future in as_completed(futures):
            try:
                future.result() # Wait for each download to complete
            except Exception as e:
                if log_cb: log_cb(f"Erro durante o processamento de um download: {e}")
    if log_cb: log_cb("Todos os downloads foram processados.")


