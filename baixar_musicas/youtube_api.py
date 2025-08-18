"""
Módulo de integração com a YouTube Data API v3 e YouTube Music API.
Busca de artista, validação e obtenção das músicas mais populares.
"""
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from ytmusicapi import YTMusic
from .utils import carregar_api_key
from .logger import get_logger

logger = get_logger('youtube_api')


def buscar_artista_youtube(artista_nome: str) -> List[Dict]:
    """
    Busca canais de artista oficiais e canais musicais no YouTube/YouTube Music.
    Retorna lista de dicts: nome, id, url, thumbnail, inscritos, categoria, oficial, fonte.
    """
    resultados = []
    # 1. Buscar artistas oficiais no YouTube Music
    try:
        ytm = YTMusic()
        artistas = ytm.search(artista_nome, filter='artists')
        for art in artistas:
            if art.get('artistId') and art.get('browseId'):
                resultados.append({
                    'nome': art['artist'],
                    'id': art['browseId'],
                    'url': f"https://music.youtube.com/channel/{art['browseId']}",
                    'thumbnail': art['thumbnails'][-1]['url'] if art.get('thumbnails') else '',
                    'inscritos': art.get('subscribers', 'N/A'),
                    'categoria': 'Música',
                    'oficial': art.get('resultType') == 'artist',
                    'fonte': 'YouTube Music'
                })
    except Exception as e:
        logger.warning(f"YTMusic falhou: {e}")

    # 2. Buscar canais no YouTube com filtros de música
    try:
        api_key = carregar_api_key()
        youtube = build('youtube', 'v3', developerKey=api_key)
        req = youtube.search().list(
            q=artista_nome,
            type='channel',
            part='snippet',
            maxResults=10
        )
        res = req.execute()
        items = res.get('items', [])
        for item in items:
            canal_id = item['id']['channelId']
            snippet = item['snippet']
            # Buscar detalhes do canal
            canal_req = youtube.channels().list(
                id=canal_id,
                part='snippet,statistics,topicDetails'
            )
            canal_res = canal_req.execute()
            if not canal_res['items']:
                continue
            canal = canal_res['items'][0]
            # Filtros: só canais com tópico de música ou categoria musical
            topicos = canal.get('topicDetails', {}).get('topicIds', [])
            categoria = 'Outro'
            if '/m/04rlf' in topicos:
                categoria = 'Música'
            elif any(t in topicos for t in ['/m/02mscn', '/m/0ggq0m', '/m/05rwpb']):
                categoria = 'Música (outro gênero)'
            if categoria == 'Outro':
                continue
            inscritos = canal.get('statistics', {}).get('subscriberCount', 'N/A')
            resultados.append({
                'nome': canal['snippet']['title'],
                'id': canal_id,
                'url': f'https://www.youtube.com/channel/{canal_id}',
                'thumbnail': canal['snippet']['thumbnails']['default']['url'],
                'inscritos': inscritos,
                'categoria': categoria,
                'oficial': 'Canal de Artista Oficial' in canal['snippet'].get('customUrl', ''),
                'fonte': 'YouTube'
            })
    except Exception as e:
        logger.error(f"YouTube API falhou: {e}")
    # Priorizar oficiais e categoria música
    resultados = sorted(resultados, key=lambda x: (x['oficial'], x['categoria']=='Música'), reverse=True)
    return resultados


def buscar_musicas_populares(canal_id: str, quantidade: int = 20) -> List[Dict]:
    """
    Busca as músicas/vídeos mais populares do canal do artista.
    Prioriza playlist oficial "Top Tracks". Se não houver, busca vídeos mais populares do canal, filtrando por categoria Música.
    Retorna lista de dicts: título, vídeo_id, url.
    """
    musicas = []
    try:
        api_key = carregar_api_key()
        youtube = build('youtube', 'v3', developerKey=api_key)
        # 1. Tentar encontrar playlist "Top Tracks"
        playlists = youtube.playlists().list(
            channelId=canal_id,
            part='snippet',
            maxResults=20
        ).execute().get('items', [])
        playlist_id = None
        for pl in playlists:
            nome = pl['snippet']['title'].lower()
            if 'top' in nome and ('músicas' in nome or 'tracks' in nome):
                playlist_id = pl['id']
                break
        if playlist_id:
            # Buscar músicas da playlist
            items = youtube.playlistItems().list(
                playlistId=playlist_id,
                part='snippet',
                maxResults=quantidade
            ).execute().get('items', [])
            for item in items:
                snippet = item['snippet']
                musicas.append({
                    'titulo': snippet['title'],
                    'video_id': snippet['resourceId']['videoId'],
                    'url': f"https://www.youtube.com/watch?v={snippet['resourceId']['videoId']}"
                })
        else:
            # Buscar vídeos mais populares do canal, filtrando por categoria Música
            search = youtube.search().list(
                channelId=canal_id,
                part='snippet',
                order='viewCount',
                maxResults=50,
                type='video'
            ).execute().get('items', [])
            video_ids = [item['id']['videoId'] for item in search]
            # Buscar detalhes dos vídeos em lotes
            for i in range(0, len(video_ids), 50):
                batch = video_ids[i:i+50]
                videos = youtube.videos().list(
                    id=','.join(batch),
                    part='snippet',
                ).execute().get('items', [])
                for v in videos:
                    categoria = v['snippet'].get('categoryId')
                    if categoria == '10':  # Música
                        musicas.append({
                            'titulo': v['snippet']['title'],
                            'video_id': v['id'],
                            'url': f"https://www.youtube.com/watch?v={v['id']}"
                        })
            musicas = musicas[:quantidade]
    except Exception as e:
        logger.error(f"Erro ao buscar músicas populares: {e}")
    return musicas
