from googleapiclient.discovery import build
import pandas as pd
API_KEY = "AIzaSyA4v7SM3a4PfpxrXfKL_nN9uEJmcZT1hH0"


youtube = build("youtube", "v3", developerKey=API_KEY)

def extract_from_youtube():
	playlists = []
	nb_videos = []
	date = []
	ids = []
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

					next_page_token = response.get("nextPageToken")
					if not next_page_token:
									break
					
	df = pd.DataFrame(list(zip(playlists, nb_videos, date, ids)))
	df.columns=["title", "number_of_videos", "created_date", "playlist_url"]
	df['created_date'] = pd.to_datetime(df['created_date']).dt.date

	df.to_csv("data/crashcourse_playlists.csv", index=False)
	print("Data extracted and saved to crashcourse_playlists.csv")
	
	return df