from googleapiclient.discovery import build
import pandas as pd
from urllib.parse import quote
import streamlit as st
API_KEY = "AIzaSyA4v7SM3a4PfpxrXfKL_nN9uEJmcZT1hH0"


youtube = build("youtube", "v3", developerKey=API_KEY)

def extractPlaylistsFromChannel():
	"""
	Le programme extrait les données de toutes les playlists d'une chaine YouTube.
	"""
	playlists = []
	nb_videos = []
	date = []
	ids = []
	descriptions = []
	miniatures = []
	next_page_token = None

	while True:
					request = youtube.playlists().list(
									part="snippet, contentDetails",
									channelId = "UCX6b17PVsYBQ0ip5gyeme-Q", #CrashCourse
									maxResults=50,
									pageToken=next_page_token
					)
					response = request.execute()

					for item in response["items"]:
									playlists.append(item["snippet"]["title"])
									nb_videos.append(item['contentDetails']['itemCount'])
									date.append(item["snippet"]["publishedAt"])
									ids.append("https://www.youtube.com/playlist?list=" + str(item["id"]))
									miniatures.append(item['snippet']['thumbnails']['default']['url'] + " ")
									descriptions.append(item['snippet']['description'])
									

					next_page_token = response.get("nextPageToken")
					if not next_page_token:
									break
					
	df = pd.DataFrame(list(zip(playlists, nb_videos, date, ids, miniatures, descriptions)))
	df.columns=["title", "number_of_videos", "created_date", "playlist_url", "miniatures", "descriptions"]
	df['created_date'] = pd.to_datetime(df['created_date']).dt.date
	df["Details de la playlist"] = df.apply(lambda x: f'<a href="/videos?playlist={x['playlist_url']}&name={quote(x['title'])}">Afficher les détails</a>', axis = 1)
	# [st.link_button("Go to gallery", "https://streamlit.io/gallery")] 
	df["playlist_url"] =  df["playlist_url"].apply(lambda x: f'<a href="{x}" target="_blank">Ouvrir</a>')
	df['miniatures'] = df['miniatures'].apply(lambda x : (f'<img src="{x}" width=190>'))

	df.to_csv("data/crashcourse_playlists.csv", index=False)
	print("Data extracted and saved to crashcourse_playlists.csv")
	
	return df
