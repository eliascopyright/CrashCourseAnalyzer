# junior_playlist_videos.py
import re, datetime
import streamlit as st
from urllib.parse import urlparse, parse_qs
import pandas as pd, os, sys
from googleapiclient.discovery import build
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.extractFromChannel as extractFromChannel

API_KEY = "AIzaSyA4v7SM3a4PfpxrXfKL_nN9uEJmcZT1hH0"  # <-- remplace par ta clé

# 1) Récupérer l'ID de la playlist (depuis l'URL ou directement)

desc = """
Welcome to Crash Course Native American History! Over the next 24 episodes, Che Jim will introduce you to the deep, ongoing history of the Indigenous peoples who’ve called these lands home from time immemorial to today."\
Course Description:
Over the course of 24 episodes, we’re going to learn about Native American history. Host Che Jim will teach you about the deep, ongoing history of Native peoples in what’s now known as the United States—from time immemorial to the Land Back movement.

This content was developed with a team of Indigenous experts, and based on an introductory college-level curriculum. By the end of this course you should be able to:
- Analyze the political and legal relationship between Native nations and the U.S. government
- Develop an informed perspective on distinct Native cultures’ traditions, practices, and worldview
- Draw connections between the past and present, in the continued existence and experiences of Native individuals and Native nations
- Highlight key figures in Native American history and illustrate their achievements and contributions

Want to know more about how this series was made? Learn more here: https://docs.google.com/document/d/17yp3u28s40TdjyrJniIf4U9YA8wPtvQ1g1B-HSHQ2Q4/edit?tab=t.0#heading=h.6vtzps565m2

***u
Support us for $5/month on Patreon to keep Crash Course free for everyone forever! https://www.patreon.com/crashcourse
Or support us directly: https://complexly.com/support
Join our Crash Course email list to get the latest news and highlights: https://mailchi.mp/crashcourse/email
Get our special Crash Course Educators newsletter: http://eepurl.com/iBgMhY

Thanks to the following patrons for their generous monthly contributions that help keep Crash Course free for everyone forever:
Duncan W Moore IV, Shruti S, Breanna Bosso, oranjeez, Kevin Knupp, Forrest Langseth, Ken Davidian, Spilmann Reed, Rie Ohta, Steve Segreto, Alan Bridgeman, Toni Miles, Krystle Young, UwU, Laurel Stevens, team dorsey, Matt Curls, Kristina D Knight, David Fanska, Barbara Pettersen, Kyle & Katherine Callahan, Bernardo Garza, Sarah & Nathan Catchings, Andrew Woods, Samantha, Jennifer Killen, Brandon Thomas, Stephen Akuffo, Leah H., Jon Allen, Jack Hart, Quinn Harden, Scott Harrison, Elizabeth LaBelle, Perry Joyce, Emily Beazley, Caleb Weeks, Constance Urist, Barrett Nuzum, Wai Jack Sin, Trevin Beattie, Alex Hackman, Katie Dean, Eric Koslow, ClareG, Ken Penttinen, Evol Hong, Stephen McCandless, Siobhán, Tandy Ratliff, Emily T, Joseph Ruf, Jason Rostoker, Les Aker, John Lee, Rizwan Kassim, Nathan Taylor, Triad Terrace, Pietro Gagliardi, Ian Dundore, Jason Buster, Indija-ka Siriwardena
__

Want to find Crash Course elsewhere on the internet?
Instagram - https://www.instagram.com/thecrashcourse/
Facebook - http://www.facebook.com/YouTubeCrashCourse
Bluesky - https://bsky.app/profile/thecrashcourse.bsky.social

CC Kids: http://www.youtube.com/crashcoursekids
"""
# 2) Créer le client YouTube
youtube = build("youtube", "v3", developerKey=API_KEY)
import re

def cleanDescriptions(desc: str):
    # 1) Les deux liens Google Docs
    prefix = re.escape("https://docs.google.com/")
    gdocs_links = re.findall(prefix + r'[^\s)"]+', desc)            

    # 2) Couper tout ce qui est pubs / remerciements (et tout après)
    #    -> on coupe dès qu’on rencontre "Sources:", "***", "Support us", "Thanks to", "Want to find"
    cut_markers = [
        'Sources:',
        'Support us',
        'Thanks to the following patrons',
        'Want to find',
    ]
    pattern = '|'.join(re.escape(m) for m in cut_markers)
    pattern = pattern + r'|\*{3,}'
    cut_re = re.compile(pattern, re.I)
    desc_clean = cut_re.split(desc)[0]

    # 3) Garder l’intro (du début jusqu’au premier chapitre)
    ts_re = re.compile(r'(?<!\d)(?:\d{1,2}:)?\d{1,2}:\d{2}(?!\d)')  # 0:52, 10:42, 1:02:10
    lines = desc_clean.replace("\r\n","\n").replace("\r","\n").splitlines()
    # print(f'\nhey there {list(ts_re.findall(desc_clean))}')
    chapters = [ln.strip() for ln in desc_clean.splitlines() if ts_re.search(ln)]
    for element in chapters: 
        element = element[::-5]
        # print(f"element je suis {element}")
    # 1) index du 1er chapitre
    m = list(ts_re.finditer(desc_clean))
    if not m:
        intro    = desc_clean.strip()
        # chapters = []
    else:
        intro    = desc_clean[:m[0].start()].strip()
        rest     = desc_clean[m[0].start():]
    return {
        "gdocs_links": gdocs_links,
        "intro": intro,
        "chapters": chapters,
    }

# --- Exemple d'usage
result = cleanDescriptions(desc)
# print("Links:", result["gdocs_links"])
# print("\nIntro:\n", result["intro"])
# print("\nChapters:")
# print("\n".join(result["chapters"]))

def parse_playlist_id(url : str) -> str | None:
    try:
        q = parse_qs(urlparse(url).query)
        st.write((q.get('list') or None)[0])
        return (q.get('list') or None)[0]
    except Exception:
        return None
# 3) Appeler playlistItems.list pour lister TOUTES les vidéos (paginer avec nextPageToken)
def UrlToDataFrame(url: str) -> tuple[pd.DataFrame, float]:
    # ... parse playlist_id ...
    videos, page_token = [], None
    playlist_id = parse_playlist_id(url)
    if not playlist_id:
        raise ValueError(f"Playlist ID introuvable dans l'URL (attendu ?list=PL...)URL passée: {url}")

    
    while True:
        res = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id, maxResults=50, pageToken=page_token
        ).execute()

        for it in res.get("items", []):
            vid = it["contentDetails"].get("videoId")
            if vid:
                videos.append({
                    "Title": it["snippet"]["title"],
                    "videoId": vid,
                    "position": it["snippet"].get("position"),
                    "publishedAt": it["contentDetails"].get("videoPublishedAt"),
                    'miniature': it['snippet']['thumbnails']['medium']["url"],
                    "videoUrl": f"https://www.youtube.com/watch?v={vid}",
                    "descriptions": cleanDescriptions(it["snippet"]["description"])['intro'],
                })

        page_token = res.get("nextPageToken")
        
        if not page_token:
            break
            
    # ---- calcul des durées (après la collecte complète) ----
    if videos:
        ids = [v["videoId"] for v in videos]
        durations = {}
        for i in range(0, len(ids), 50):
            resp = youtube.videos().list(part="contentDetails", id=",".join(ids[i:i+50])).execute()
            for x in resp.get("items", []):
                durations[x["id"]] = x["contentDetails"].get("duration")

        def iso_to_seconds(iso):
            import re
            if not iso: return None
            m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
            if not m: return None
            h,mn,s = (int(t) if t else 0 for t in m.groups())
            return h*3600 + mn*60 + s

        for v in videos:
            dur = durations.get(v["videoId"])
            v["duration"] = dur
            v["durationSeconds"] = iso_to_seconds(dur)

    df = pd.DataFrame(videos)
    df["publishedAt"] = pd.to_datetime(df["publishedAt"], errors="coerce").dt.date
    df["duration_hms"] = df["durationSeconds"].apply(
        lambda x: str(datetime.timedelta(seconds=int(x))) if pd.notnull(x) else None
    )
    df['descriptions'] = df['descriptions'].str.replace('\n', '<br>')
    total_seconds = df['durationSeconds'].sum()
    total_playlist_time = str(datetime.timedelta(seconds = float(total_seconds)))
    df.drop('durationSeconds', axis = 1, inplace = True)
    df.drop('videoId', axis = 1, inplace = True)
    
    df["videoUrl"] = df["videoUrl"].apply(lambda x: f'<a href="{x}" target="_blank">Ouvrir</a>')
    df['miniature'] = df['miniature'].apply(lambda image: f'<img src="{image}">')

    if "position" in df.columns:
        df = df.sort_values("position").reset_index(drop=True)
    df.drop('duration', axis = 1, inplace = True)
    return df , total_playlist_time
    
        
    
 
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

 # Sauvegarde CSV (décommente si tu veux)
 # df.to_csv("videos_playlist.csv", index=False, encoding="utf-8")
 
def getDescriptionFromPlaylist(url: str) -> str:
    """
    Prend une Url de playlist YouTube en entrée. Renvoie un str de la description de la playlist.
    
    """
    playlist_id = url.split("=")[1]
    page_token = None

    req = youtube.playlists().list(
    part="snippet,contentDetails",
    id=playlist_id,
    )
    res = req.execute()
    description = res['items'][0]['snippet']['description']

    return description
def miniatureFromPlaylist(url:str) ->str:
    playlist_id = url.split('=')[1]
    req  = youtube.playlists().list(
    id = playlist_id,
    part = 'snippet, contentDetails')
    res = req.execute()
    image = res['items'][0]['snippet']['thumbnails']['high']['url']
    return image

 
# url ="https://www.youtube.com/playlist?list=PL8dPuuaLjXtNNaritQa7QqwEJeQHH0TxX"

# df = UrlToDataFrame(url)[0]
# image = miniatureFromPlaylist(url)
# description_playlist = getDescriptionFromPlaylist(url)
# sources = f'<a href="{cleanDescriptions(url)["gdocs_links"]}" target=_blank> Sources</a>'
