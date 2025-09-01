import streamlit as st, os, sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
#print(f"****************************************{os.listdir()}************************")

from core import extractFromChannel
from components import kpis
from components import tableau
from components import topn

st.set_page_config(
				page_title="Crash Course Analyzer",
				page_icon="📊",
				layout="wide",
				initial_sidebar_state="expanded",
)
# first_container = st.container(
# 	horizontal=True,
# )

# second_container = st.container(
# 	horizontal=True,
# )
# st.title("Crash Course Analyzer")

# if st.button("Extract Data from YouTube"):
# 	with st.spinner("Extracting data..."):
# 		df = extract.extractPlaylistsFromChannel()
# 		st.success("Data extracted successfully!")

# 	with first_container:
# 		st.metric("Total Playlists", df.shape[0], width=200)
# 		st.metric("Playlist with most videos", str(df['Playlist'][df['Number of videos'] == df['Number of videos'].max()]), width=500)
# 		st.metric("Playlist with less videos", str(df['Playlist'][df['Number of videos'] == df['Number of videos'].min()]), width=500)
		

# 	with second_container:
# 		st.dataframe(df)

# 		st.bar_chart(df, x = "Date created", y =	"Number of videos", x_label= "Date", y_label="Number of videos")


# app/app.py

# ---- config UI ----
st.set_page_config(page_title="CrashCourse Playlists Analyzer", page_icon="🎬", layout="wide")

channel_page = st.Page("./pages/channel.py", title="From Channel", icon=None)
videos_page = st.Page("./pages/playlist.py", title="From Playlist", icon=None)

pg = st.navigation([channel_page, videos_page])
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
pg.run()
