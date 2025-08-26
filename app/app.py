import streamlit as st, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import extract
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
# 		df = extract.extract_from_youtube()
# 		st.success("Data extracted successfully!")

# 	with first_container:
# 		st.metric("Total Playlists", df.shape[0], width=200)
# 		st.metric("Playlist with most videos", str(df['Playlist'][df['Number of videos'] == df['Number of videos'].max()]), width=500)
# 		st.metric("Playlist with less videos", str(df['Playlist'][df['Number of videos'] == df['Number of videos'].min()]), width=500)
		

# 	with second_container:
# 		st.dataframe(df)

# 		st.bar_chart(df, x = "Date created", y =	"Number of videos", x_label= "Date", y_label="Number of videos")


# app/app.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import streamlit as st

# ---- import du core ----
from core import extract  # doit exposer get_channel_playlists() et (optionnel) count_videos()

# ---- config UI ----
st.set_page_config(page_title="CrashCourse Playlists Analyzer", page_icon="🎬", layout="wide")

# ---- helpers cache ----
@st.cache_data
def _get_playlists_cached() -> pd.DataFrame:
    df = extract.extract_from_youtube()
    # hygiène
    st.write(f"Colonnes extraites : {df.columns.tolist()}")
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    for col in ["title", "number_of_videos", "playlist_url', 'created_date"]:
        if col not in df.columns:
            df[col] = None
    df["title"] = df["title"].fillna("").str.strip()
    print(df.columns)
    return df

def _count_one(url_or_id: str) -> int | None:
    try:
        if hasattr(extract, "count_videos"):
            return extract.count_videos(url_or_id)
        # fallback: si pas de fonction dispo, renvoie None (la colonne restera vide)
        return None
    except Exception:
        return None

   
# ---- sidebar ----
with st.sidebar:
    st.header("Paramètres")
    url = st.text_input(
        "URL de l’onglet Playlists",
        value="https://www.youtube.com/channel/UCX6b17PVsYBQ0ip5gyeme-Q/",
        help="Colle l’URL /@handle/playlists ou /channel/UC.../playlists",
    )
    do_count = st.toggle("Compter les vidéos par playlist", value=True)
    top_n = st.number_input("Top N (par nb de vidéos)", min_value=1, value=20, step=1)
    st.divider()
    run = st.button("Analyser")

st.title("CrashCourse Playlists Analyzer")
st.caption("Analyse des playlists d’une chaîne YouTube • extraction via core.extract • cache & parallélisme")

if not run:
    st.info("Renseigne l’URL (par défaut CrashCourse) puis clique **Analyser**.")
    st.stop()

# ---- main flow ----
try:
    with st.spinner("Extraction des playlists…"):
        df = _get_playlists_cached()
except Exception as e:
    st.error(f"Échec d’extraction : {e}")
    st.stop()

if df.empty:
    st.warning("Aucune playlist trouvée. Vérifie l’URL (onglet *Playlists*).")
    st.stop()

st.success(f"{len(df)} playlists détectées.")

# comptage (optionnel)
if do_count:
    st.write("📊 Comptage des vidéos par playlist…")
    urls = df["number_of_videos"].tolist()

# filtres rapides
colA, colB, colC, _ = st.columns([2, 2, 2, 1])
with colA:
    q = st.text_input("🔎 Filtrer (titre contient…)", value="")
with colB:
    has_count = st.selectbox("Filtre nb vidéos", ["Tous", "Avec compteur", "Sans compteur"])
with colC:
    sort_mode = st.selectbox("Tri", ["Par nb vidéos (desc)", "Par titre (A→Z)"])

df_view = df.copy()
if q:
    df_view = df_view[df_view["title"].str.contains(q, case=False, na=False)]

if has_count == "Avec compteur":
    df_view = df_view[df_view["number_of_videos"].notna()]
elif has_count == "Sans compteur":
    df_view = df_view[df_view["number_of_videos"].isna()]

# tri
if sort_mode.startswith("Par nb vidéos") and df_view["number_of_videos"].notna().any():
    df_view = df_view.sort_values(["number_of_videos", "title"], ascending=[False, True])
else:
    df_view = df_view.sort_values("title")

# KPIs
total_playlists = len(df_view)
total_videos = int(df_view["number_of_videos"].fillna(0).sum())
c1, c2, c3 = st.columns(3)
c1.metric("Playlists", f"{total_playlists}")
c2.metric("Vidéos (somme)", f"{total_videos:,}".replace(",", " "))
c3.metric("Source", "core.extract")

st.divider()

# tableau
st.subheader("Tableau des playlists")
show_cols = ["title", "number_of_videos", "playlist_url", "created_date"]
for c in show_cols:
    if c not in df_view.columns:
        df_view[c] = None
st.dataframe(df_view[show_cols].reset_index(drop=True), use_container_width=True)

# top N chart
if df_view["number_of_videos"].notna().any():
    st.subheader(f"Top {min(top_n, len(df_view))} playlists par nombre de vidéos")
    top_df = df_view.dropna(subset=["number_of_videos"]).nlargest(int(top_n), "number_of_videos")[["title", "number_of_videos"]]
    top_df = top_df.set_index("title")
    st.bar_chart(top_df)

# export
csv = df_view[show_cols].to_csv(index=False).encode("utf-8")
st.download_button("💾 Télécharger CSV", data=csv, file_name="playlists.csv", mime="text/csv")

