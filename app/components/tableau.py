import streamlit as st
import pandas as pd

# tableau
def show_table(df_view):
	st.subheader("Tableau des playlists")
	show_cols = ["title", "number_of_videos", "playlist_url", "created_date"]
	for c in show_cols:
					if c not in df_view.columns:
									df_view[c] = None
	st.write(df_view.to_html(escape=False, index=False), unsafe_allow_html=True)