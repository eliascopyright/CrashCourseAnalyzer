# junior_playlist_videos.py
import re, datetime
from urllib.parse import urlparse, parse_qs

import pandas as pd
from googleapiclient.discovery import build

API_KEY = "AIzaSyA4v7SM3a4PfpxrXfKL_nN9uEJmcZT1hH0"  # <-- remplace par ta clé

# 1) Récupérer l'ID de la playlist (depuis l'URL ou directement)
def get_playlist_id(s: str) -> str:
    if s.startswith("http"):
        qs = parse_qs(urlparse(s).query)
        return qs.get("list", [""])[0]
    return s

# 2) Créer le client YouTube
youtube = build("youtube", "v3", developerKey=API_KEY)

# 3) Appeler playlistItems.list pour lister TOUTES les vidéos (paginer avec nextPageToken)
def getplaylistItems(PLAYLIST : str) -> list:
	"""
	Takes a playlist URL, returns a list of videos
	"""
	playlist_id = get_playlist_id(PLAYLIST)
	videos = []
	page_token = None

	while True:
					req = youtube.playlistItems().list(
									part="snippet,contentDetails",
									playlistId=playlist_id,
									maxResults=50,
									pageToken=page_token,
					)
					res = req.execute()

					for item in res.get("items", []):
									title = item["snippet"]["title"]
									vid = item["contentDetails"].get("videoId")
									position = item["snippet"].get("position")
									published_at = item["contentDetails"].get("videoPublishedAt")
									if vid:
													videos.append({
																	"title": title,
																	"videoId": vid,
																	"position": position,
																	"publishedAt": published_at,
																	"videoUrl": f"https://www.youtube.com/watch?v={vid}",
													})

					page_token = res.get("nextPageToken")
					if not page_token:
									break
	return videos

# 4) (Option) récupérer la durée des vidéos (videos.list avec contentDetails)
#    Simple: on boucle par paquets de 50 IDs (limite API)
def iso_to_seconds(iso):
    if not iso:
        return None
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not m: 
        return None
    h, mn, s = (int(x) if x else 0 for x in m.groups())
    return h*3600 + mn*60 + s

def getDataFrameVideos(videos: list) -> pd.DataFrame:
	"""
	From a return of getplaylistItems: returns DataFrame
	"""
	if videos:
					ids = [v["videoId"] for v in videos]
					durations = {}
					for i in range(0, len(ids), 50):
									chunk = ids[i:i+50]
									resp = youtube.videos().list(
													part="contentDetails", id=",".join(chunk), maxResults=50
									).execute()
									for it in resp.get("items", []):
													durations[it["id"]] = it["contentDetails"].get("duration")

					# ajouter la durée au tableau
					for v in videos:
									dur = durations.get(v["videoId"])
									v["duration"] = dur
									v["durationSeconds"] = iso_to_seconds(dur)
						
			# 5) Mettre en DataFrame et trier par position
	df = pd.DataFrame(videos)
	
	df['publishedAt'] = pd.to_datetime(df['publishedAt']).dt.date
	df.drop('duration', axis = 1, inplace = True)
	df.drop('videoId', axis = 1, inplace = True)
	df['durationSeconds'] = df['durationSeconds'].apply(lambda x: str(datetime.timedelta(seconds = x)))

	df['videoUrl'] = df['videoUrl'].apply(lambda x: f'<a href="{x}" target="_blank">Ouvrir</a>')
	if "position" in df.columns:
					df = df.sort_values("position").reset_index(drop=True)
			


	print(df.head())
	return df
	# Sauvegarde CSV (décommente si tu veux)
	# df.to_csv("videos_playlist.csv", index=False, encoding="utf-8")
