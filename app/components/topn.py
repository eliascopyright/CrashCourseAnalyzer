import streamlit as st
import pandas as pd
# top N chart
def topnchart(df_view: pd.DataFrame, top_n: int):

	if df_view["number_of_videos"].notna().any():
					st.subheader(f"Top {min(top_n, len(df_view))} playlists par nombre de vidéos")
					top_df = df_view.dropna(subset=["number_of_videos"]).nlargest(int(top_n), "number_of_videos")[["title", "number_of_videos"]]
					top_df = top_df.set_index("title")
					st.bar_chart(top_df)