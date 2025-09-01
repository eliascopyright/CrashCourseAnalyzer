import streamlit as st, os, sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
#print(f"****************************************{os.listdir()}************************")

from core import extractFromChannel
from components import kpis
from components import tableau
from components import topn

# ---- helpers cache ----
@st.cache_data
def _get_playlists_cached() -> pd.DataFrame:
    df = extractFromChannel.extractPlaylistsFromChannel()
    # hygiène
    st.write(f"Colonnes extraites : {df.columns.tolist()}")
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    for col in ["title", "number_of_videos", "playlist_url", "created_date", "Details de la playlist"]:
        if col not in df.columns:
            df[col] = None
    df["title"] = df["title"].fillna("").str.strip()
    print(df.columns)
    return df

def _count_one(url_or_id: str) -> int | None:
    try:
        if hasattr(extractFromChannel, "count_videos"):
            return extractFromChannel.count_videos(url_or_id)
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
        help="Colle l’URL /channel/UC....",
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

kpis.print_kpis(df_view)

st.divider()
tableau.show_table(df_view)

topn.topnchart(df_view, top_n)

# export
# csv = df_view[show_cols].to_csv(index=False).encode("utf-8")
# st.download_button("💾 Télécharger CSV", data=csv, file_name="playlists.csv", mime="text/csv")

