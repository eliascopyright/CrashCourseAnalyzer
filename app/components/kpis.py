import streamlit as st,datetime
import pandas as pd

def print_kpis(df_view : pd.DataFrame):
# KPIs
	total_playlists = len(df_view)
	total_videos = int(df_view["number_of_videos"].fillna(0).sum())
	c1, c2, c3 = st.columns(3)
	c1.metric("Playlists", f"{total_playlists}")
	c2.metric("Vidéos (somme)", f"{total_videos:,}".replace(",", " "))