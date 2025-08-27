import streamlit as st,sys, os, json, pandas as pd, datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from core import extract_videos_from_playlists

st.title("Bonjour à tous")
params = st.query_params  
# st.title(params.playlist)

# extract_videos_from_playlists.getplaylistItems(params['playlist'])
urlpourtester = "https://www.youtube.com/playlist?list=PL8dPuuaLjXtOVe7Q88hA-IJ1l6BkzxxDC"
videos = extract_videos_from_playlists.getplaylistItems(urlpourtester)
df = extract_videos_from_playlists.getDataFrameVideos(videos)




print(df.head())


st.dataframe(df)