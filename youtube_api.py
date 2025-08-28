import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from utils import load_environment
import re
import subprocess
import json

load_environment()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_video_details(youtube, video_ids):
    """Obtém detalhes (duração e visualizações) para uma lista de IDs de vídeo."""
    details = {}
    if not video_ids:
        return details
    try:
        response = youtube.videos().list(
            part="contentDetails,statistics",
            id=",".join(video_ids)
        ).execute()
        for item in response.get("items", []):
            video_id = item["id"]
            duration = item["contentDetails"]["duration"]
            views = item["statistics"].get("viewCount", "0")
            details[video_id] = {
                "duration": duration,
                "views": views
            }
    except HttpError as e:
        print(f"Erro HTTP ao obter detalhes do vídeo: {e.resp.status} - {e.content}")
    except Exception as e:
        print(f"Erro inesperado ao obter detalhes do vídeo: {e}")
    return details

def parse_duration(duration_str):
    """Converte a duração do formato ISO 8601 para um formato legível (H:MM:SS ou MM:SS)."""
    hours = 0
    minutes = 0
    seconds = 0
    
    if 'H' in duration_str:
        hours = int(re.search(r'(\d+)H', duration_str).group(1))
    if 'M' in duration_str:
        minutes = int(re.search(r'(\d+)M', duration_str).group(1))
    if 'S' in duration_str:
        seconds = int(re.search(r'(\d+)S', duration_str).group(1))
        
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    if total_seconds < 60:
        return f"0:{seconds:02d}"
    elif total_seconds < 3600:
        return f"{minutes}:{seconds:02d}"
    else:
        return f"{hours}:{minutes:02d}:{seconds:02d}"

def search_videos_yt_dlp(query, limit):
    """Realiza a busca de vídeos usando yt-dlp como fallback."""
    try:
        command = ["yt-dlp", "--flat-playlist", "--dump-json", f"ytsearch{limit}:{query}"]
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        
        results = []
        for line in process.stdout.splitlines():
            try:
                data = json.loads(line)
                # Filter out non-video items if any, and ensure basic info is present
                if data.get("_type") == "video" and data.get("id"):
                    results.append({
                        "title": data.get("title", "N/A"),
                        "url": data.get("webpage_url", f"https://www.youtube.com/watch?v={data["id"]}"),
                        "channelTitle": data.get("channel", "N/A"),
                        "videoId": data["id"],
                        "duration": str(data.get("duration", "N/A")), # Duration in seconds
                        "views": str(data.get("view_count", "N/A")) # Views as string
                    })
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON do yt-dlp: {e}")
                continue
        return results
    except subprocess.CalledProcessError as e:
        print(f"A busca com yt-dlp falhou: {e.stderr}")
        return []
    except FileNotFoundError:
        print("yt-dlp não encontrado. Certifique-se de que está instalado e no PATH.")
        return []
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a busca com yt-dlp: {e}")
        return []

def search_videos(artist: str, limit: int, min_views: int = 0) -> list[dict]:
    """Busca vídeos do YouTube com base no artista e filtros."""
    if not YOUTUBE_API_KEY:
        print("Chave da API do YouTube não configurada. Usando yt-dlp como fallback.")
        yt_dlp_results = search_videos_yt_dlp(artist, limit)
        for video in yt_dlp_results:
            if video["views"] != "N/A":
                video["views"] = int(video["views"])
        filtered_yt_dlp_results = [v for v in yt_dlp_results if v["views"] != "N/A" and v["views"] >= min_views]
        return filtered_yt_dlp_results

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    all_results = []

    # Try searching with \'music\' appended first
    queries = [f"{artist} music", artist]

    for query in queries:
        try:
            search_response = youtube.search().list(
                q=query,
                part="id,snippet",
                maxResults=limit,
                type="video",
                videoCategoryId="10" # Music category
            ).execute()

            current_query_results = []
            video_ids_for_details = []

            for item in search_response.get("items", []):
                if "videoId" in item["id"]:
                    video_ids_for_details.append(item["id"]["videoId"])
                    current_query_results.append({
                        "title": item["snippet"]["title"],
                        "url": f"https://www.youtube.com/watch?v={item["id"]["videoId"]}",
                        "channelTitle": item["snippet"]["channelTitle"],
                        "videoId": item["id"]["videoId"],
                        "duration": "N/A", # Placeholder
                        "views": "N/A", # Placeholder
                        "channelId": item["snippet"]["channelId"]
                    })
            
            # Get video details (duration and views)
            if video_ids_for_details:
                video_details = get_video_details(youtube, video_ids_for_details)
                for video in current_query_results:
                    detail = video_details.get(video["videoId"])
                    if detail:
                        video["duration"] = parse_duration(detail["duration"])
                        video["views"] = int(detail["views"]) # Store as int for filtering

            # Filter by min_views and prioritize verified channels
            filtered_results = []
            verified_channels = []
            other_channels = []

            for video in current_query_results:
                if video["views"] != "N/A" and video["views"] >= min_views:
                    # This is a simplified check for verified channels. A more robust solution
                    # would involve checking the channel\\\"s badges via the YouTube API if available,
                    # or maintaining a list of known official channels.
                    if "VEVO" in video["channelTitle"].upper() or "OFFICIAL" in video["channelTitle"].upper():
                        verified_channels.append(video)
                    else:
                        other_channels.append(video)
            
            # Combine results, prioritizing verified channels
            all_results.extend(verified_channels)
            all_results.extend(other_channels)

            if all_results: # If we found results with \'music\', break and use them
                break

        except HttpError as e:
            print(f"Erro HTTP ao buscar vídeos: {e.resp.status} - {e.content}")
            # Fallback to yt-dlp if API fails for the second query as well
            if query == artist: # Only fallback if the generic artist search also failed
                print("YouTube API search failed. Tentando fallback com yt-dlp.")
                yt_dlp_results = search_videos_yt_dlp(artist, limit)
                # Convert views to int for filtering
                for video in yt_dlp_results:
                    if video["views"] != "N/A":
                        video["views"] = int(video["views"])
                # Filter yt-dlp results by min_views
                filtered_yt_dlp_results = [v for v in yt_dlp_results if v["views"] != "N/A" and v["views"] >= min_views]
                return filtered_yt_dlp_results
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            return []

    # Format views back to string with commas for display
    for video in all_results:
        if isinstance(video["views"], int):
            video["views"] = f"{video["views"]:,}"

    return all_results


