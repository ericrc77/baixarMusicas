"""
Módulo para buscar artistas e músicas populares usando YouTube Data API v3 e ytmusicapi.
"""

import os
from typing import List
from ytmusicapi import YTMusic
from googleapiclient.discovery import build
from dotenv import load_dotenv
from src.models.artist import Artist
from src.models.music import Music

load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

def buscar_artista_youtube(nome_artista: str) -> List[Artist]:
    """Busca artistas/cantores/bandas no YouTube (com imagem e inscritos)."""
    if not YOUTUBE_API_KEY:
        raise Exception('YOUTUBE_API_KEY não configurada no .env')
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    search = youtube.search().list(
        part='snippet', q=nome_artista, type='channel', maxResults=10
    ).execute()
    canais = []
    for item in search.get('items', []):
        channel_id = item['snippet']['channelId']
        # Buscar detalhes do canal
        channel = youtube.channels().list(
            part='snippet,statistics,topicDetails', id=channel_id
        ).execute()
        if not channel['items']:
            continue
        ch = channel['items'][0]
        # Filtro: só canais de música (topicId de música ou nome relacionado)
        topics = ch.get('topicDetails', {}).get('topicIds', [])
        is_music = any(t in topics for t in ['/m/04rlf', '/m/02mscn', '/m/0ggq0m', '/m/05rwpb'])
        title = ch['snippet']['title']
        if not is_music and not any(x in title.lower() for x in ['music', 'música', 'banda', 'cantor', 'rapper', 'dj']):
            continue
        thumb = ch['snippet']['thumbnails']['default']['url']
        subs = int(ch['statistics'].get('subscriberCount', 0))
        artistas = Artist(
            name=title,
            channel_id=channel_id,
            subscribers=subs,
            category='Música',
            is_official=False,
        )
        # Adiciona campo extra para thumbnail (não está no dataclass padrão)
        artistas.thumbnail = thumb
        canais.append(artistas)
    return canais

def buscar_musicas_populares(channel_id: str, quantidade: int = 20) -> List[Music]:
    """Busca as músicas mais populares do canal oficial do artista usando YouTube Data API v3."""
    if not YOUTUBE_API_KEY:
        raise Exception('YOUTUBE_API_KEY não configurada no .env')
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    # Buscar playlist "Top Tracks" do canal
    playlists = youtube.playlists().list(
        part='snippet', channelId=channel_id, maxResults=10
    ).execute()
    top_playlist_id = None
    for pl in playlists.get('items', []):
        if 'top' in pl['snippet']['title'].lower():
            top_playlist_id = pl['id']
            break
    musicas = []
    if top_playlist_id:
        # Buscar músicas da playlist
        items = youtube.playlistItems().list(
            part='snippet', playlistId=top_playlist_id, maxResults=quantidade
        ).execute()
        for item in items.get('items', []):
            snippet = item['snippet']
            musicas.append(Music(
                title=snippet['title'],
                video_id=snippet['resourceId']['videoId'],
                url=f"https://www.youtube.com/watch?v={snippet['resourceId']['videoId']}"
            ))
    else:
        # Buscar vídeos mais populares do canal
        videos = youtube.search().list(
            part='snippet', channelId=channel_id, maxResults=quantidade, order='viewCount', type='video', videoCategoryId='10'
        ).execute()
        for v in videos.get('items', []):
            musicas.append(Music(
                title=v['snippet']['title'],
                video_id=v['id']['videoId'],
                url=f"https://www.youtube.com/watch?v={v['id']['videoId']}"
            ))
    return musicas
