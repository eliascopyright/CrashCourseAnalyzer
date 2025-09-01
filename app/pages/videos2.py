import streamlit as st, sys, os, pandas as pd, datetime

# Chemins d'import locaux
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from core import extractFromPlaylist  # (extractFromChannel non utilisé ici)

# --------- Page config + petit CSS ---------
st.set_page_config(page_title="Vision par vidéo", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
svg[data-testid="stFileUploaderIcon"] { display: none; }
</style>
""", unsafe_allow_html=True)
st.markdown('<img src="https://www.svgrepo.com/show/503047/link.svg" width="30">', unsafe_allow_html=True)

# --------- Utils ---------
def qp_str(params, key, default=""):
    v = params.get(key, default)
    if isinstance(v, list):
        return v[0] if v else default
    return v

def minutes_from_hms(x):
    if not x or pd.isna(x):
        return None
    h, m, s = map(int, str(x).split(":"))
    return h*60 + m + s/60

# --------- Récup URL & nom ---------
params = st.query_params
url  = qp_str(params, "playlist", "")
name = qp_str(params, "name", "Sans nom")

if not url:
    url = st.chat_input("URL de la playlist à analyser :", key="playlist_url")

if not url:
    st.title(f"Détails pour la playlist de CrashCourse : {name}")
    st.info("Collez l'URL de la playlist (?list=PL...) pour commencer.")
    st.stop()

# --------- Chargement des données ---------
try:
    res = extractFromPlaylist.UrlToDataFrame(url)
    if not res or not isinstance(res, tuple) or len(res) != 2:
        st.error("URL invalide ou impossible de lire la playlist (attendu ?list=PL...).")
        st.stop()

    df, total_time = res
    image_url = extractFromPlaylist.miniatureFromPlaylist(url)
    description_playlist = extractFromPlaylist.getDescriptionFromPlaylist(url)
    sources_url = extractFromPlaylist.cleanDescriptions(url)["gdocs_links"]
except Exception as e:
    st.title(f"Détails pour la playlist de CrashCourse : {name}")
    st.error(f"Erreur lors du chargement de la playlist : {e}")
    st.stop()

if df.empty:
    st.title(f"Détails pour la playlist de CrashCourse : {name}")
    st.warning("Aucune vidéo trouvée pour cette playlist.")
    st.stop()

# --------- En-tête ---------
st.title(f"Détails pour la playlist de CrashCourse : {name}")

# --------- Carte description + sources ---------
with st.container(border=True):
    cols = st.columns([1, 2])
    with cols[0]:
        st.markdown(f'<img src="{image_url}" style="max-width:100%;">', unsafe_allow_html=True)
    with cols[1]:
        st.write(description_playlist)
        st.markdown(f'<a href="{sources_url}" target="_blank">Sources</a>', unsafe_allow_html=True)

# --------- Tuiles de synthèse ---------
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Nombre de vidéos", df.shape[0])
with c2:
    st.metric("Durée totale", str(total_time))
with c3:
    st.metric("Première publication", str(df["publishedAt"].min()))

st.divider()

# --------- Filtres ---------
with st.expander("Filtres"):
    colf1, colf2, colf3 = st.columns([2, 1, 1])
    with colf1:
        q = st.text_input("Filtrer par mot dans le titre :", "")
    with colf2:
        min_dur = st.number_input("Durée min (minutes)", min_value=0, value=0)
    with colf3:
        max_dur = st.number_input("Durée max (minutes)", min_value=0, value=0)

df["_minutes"] = df["duration_hms"].apply(minutes_from_hms)

mask = pd.Series(True, index=df.index)
if q:
    mask &= df["Title"].str.contains(q, case=False, na=False)
if min_dur > 0:
    mask &= df["_minutes"].fillna(0) >= min_dur
if max_dur > 0:
    mask &= df["_minutes"].fillna(0) <= max_dur

df_filtered = df[mask].drop(columns=["_minutes"])

# --------- Player intégré ---------
with st.expander("▶️ Lire une vidéo ici"):
    # On extrait l'URL du lien HTML contenu dans la colonne videoUrl
    hrefs = df_filtered["videoUrl"].str.extract(r'href="([^"]+)"', expand=False)
    choices = dict(zip(df_filtered["Title"], hrefs))
    sel_title = st.selectbox("Sélectionne une vidéo", list(choices.keys()))
    if sel_title:
        st.video(choices[sel_title])

# --------- Stats visuelles ---------
with st.expander("📈 Statistiques"):
    st.write("Publications dans le temps")
    st.line_chart(df_filtered.groupby("publishedAt").size())

st.divider()

# --------- Tableau HTML (liens + miniatures conservés) ---------
st.subheader("Vidéos")
st.write(df_filtered.to_html(escape=False, index=False), unsafe_allow_html=True)

# --------- Sidebar (écho) ---------
with st.sidebar:
    st.caption("Paramètres")
    st.write(f"Nom : **{name}**")
    st.write("URL playlist :")
    st.code(url, language="text")
