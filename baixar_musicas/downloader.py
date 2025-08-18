
"""
Módulo de download de músicas/vídeos do YouTube usando yt-dlp.
Suporte a progresso, logs, concorrência, retries e robustez.
"""
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional, List, Dict
from .logger import get_logger

try:
	import yt_dlp
except ImportError:
	yt_dlp = None

MAX_WORKERS = 3
MAX_RETRIES = 3
TIMEOUT = 60  # segundos
BACKOFF_BASE = 2

logger = get_logger('downloader')

def arquivo_existe(pasta: str, titulo: str, formato: str) -> bool:
	"""Verifica se o arquivo já existe (evita duplicatas)."""
	for ext in (formato, formato.lower()):
		caminho = os.path.join(pasta, f'{titulo}.{ext}')
		if os.path.exists(caminho):
			return True
	return False

def baixar_musica(
	url: str,
	pasta_destino: str,
	formato: str = 'mp3',
	qualidade_audio: str = '320k',
	qualidade_video: str = '720',
	progresso_callback: Optional[Callable[[float, str], None]] = None,
	log_func: Optional[Callable[[str], None]] = None,
	timeout: int = TIMEOUT
) -> bool:
	"""
	Baixa uma música/vídeo do YouTube usando yt-dlp, com suporte a progresso e timeout.
	Retorna True se sucesso, False se falhou.
	"""
	if yt_dlp is None:
		msg = 'yt-dlp não está instalado.'
		if log_func:
			log_func(msg)
		logger.error(msg)
		return False
	titulo = None
	def hook(d):
		nonlocal titulo
		if d.get('status') == 'downloading':
			percent = d.get('downloaded_bytes', 0) / max(d.get('total_bytes', 1), 1)
			if progresso_callback:
				progresso_callback(percent, d.get('filename', ''))
		if d.get('status') == 'finished':
			if progresso_callback:
				progresso_callback(1.0, d.get('filename', ''))
			titulo = d.get('filename')
	ydl_opts = {
		'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'),
		'quiet': True,
		'noprogress': False,
		'nooverwrites': True,
		'ignoreerrors': True,
		'progress_hooks': [hook],
		'socket_timeout': timeout,
	}
	if formato == 'mp3':
		ydl_opts.update({
			'format': 'bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': qualidade_audio.replace('k','')
			}],
			'audio-quality': qualidade_audio,
		})
	else:
		ydl_opts.update({
			'format': f'bestvideo[height<={qualidade_video}]+bestaudio/best[height<={qualidade_video}]',
			'merge_output_format': 'mp4',
		})
	try:
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			ydl.download([url])
		return True
	except Exception as e:
		msg = f'Erro ao baixar: {e}'
		if log_func:
			log_func(msg)
		logger.error(msg)
		return False

def baixar_varias_musicas(
	musicas: List[Dict],
	pasta_destino: str,
	formato: str = 'mp3',
	log_func: Optional[Callable[[str], None]] = None,
	progresso_callback: Optional[Callable[[int, float, str], None]] = None
) -> None:
	"""
	Baixa várias músicas em paralelo, com limite de concorrência, retry e logs.
	progresso_callback(idx, percent, titulo)
	"""
	def tarefa(idx, m):
		url = m['url']
		titulo = m['titulo'].replace('/', '_').replace('\\', '_')
		for tentativa in range(1, MAX_RETRIES+1):
			if arquivo_existe(pasta_destino, titulo, formato):
				msg = f"Já existe: {titulo}.{formato} (pulando)"
				if log_func:
					log_func(msg)
				logger.info(msg)
				return 'skip'
			msg = f"Iniciando download: {titulo} (tentativa {tentativa})"
			if log_func:
				log_func(msg)
			logger.info(msg)
			sucesso = baixar_musica(
				url, pasta_destino, formato=formato,
				progresso_callback=lambda p, f: progresso_callback(idx, p, titulo) if progresso_callback else None,
				log_func=log_func
			)
			if sucesso:
				msg = f"Sucesso: {titulo}"
				if log_func:
					log_func(msg)
				logger.info(msg)
				return 'ok'
			else:
				msg = f"Falha ao baixar {titulo} (tentativa {tentativa})"
				if log_func:
					log_func(msg)
				logger.error(msg)
				time.sleep(BACKOFF_BASE ** tentativa)
		msg = f"Falha permanente: {titulo}"
		if log_func:
			log_func(msg)
		logger.error(msg)
		return 'fail'

	with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
		futuros = [executor.submit(tarefa, idx, m) for idx, m in enumerate(musicas)]
		for f in as_completed(futuros):
			pass  # progresso e logs já tratados

