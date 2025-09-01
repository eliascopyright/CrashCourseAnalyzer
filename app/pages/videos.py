import streamlit as st,sys, os, json, pandas as pd, datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from core import extractFromChannel, extractFromPlaylist

st.set_page_config(
   page_title='Vision par vidéo',
   layout="wide",
   initial_sidebar_state="expanded"
)
st.markdown("""
 <style>
 svg[data-testid="stFileUploaderIcon"] {
   display: none;
 }
 </style>
 """, unsafe_allow_html=True)

st.markdown(
 '<img src="https://www.svgrepo.com/show/503047/link.svg" width="30">', unsafe_allow_html=True
)
def qp_str(params, key, default =""):
  v = params.get(key, default)
  if isinstance(v, list):
    return v[0] if v else default
  return v


def getURL(params):
    # 1. Essaye de récupérer dans les query params
    url = qp_str(params, "playlist", "")
    name = qp_str(params, "name", "Sans nom")

    # 2. Sinon demande à l'utilisateur
    if not url:
        url = st.chat_input("URL de la playlist à analyser :", key="url")
        if url:
            st.container(height=100).chat_message("user").write(url)

    # 3. Si toujours rien → on arrête ici
    if not url:
        st.info("Collez l'URL de la playlist pour commencer.")
        st.stop()

    return url

  
url = st.chat_input("URL de la playlist à analyser :", key="url")
if url:
  # st.title(params.playlist)

  # extract_videos_from_playlists.PlaylistToVideos(params['playlist'])
  df = extractFromPlaylist.UrlToDataFrame(url)[0]
  image = extractFromPlaylist.miniatureFromPlaylist(url)
  description_playlist = extractFromPlaylist.getDescriptionFromPlaylist(url)
  sources = f'<a href="{extractFromPlaylist.cleanDescriptions(url)["gdocs_links"]}" target=_blank> Sources</a>'
  # description de la playlist  pour la mettre dans une carte (metric)

  description_container = st.container(
    border = True,
    horizontal=True
    
  )
  sources_container = st.container(
    
  )
  table_container = st.container(
    horizontal= True
  )
  cards_container = st.container(
    horizontal = True
  )
  with description_container:
    
    st.markdown(f'<img src="{image}">', unsafe_allow_html=True)
    st.write(description_playlist)

  with sources_container:
    st.write(sources, unsafe_allow_html=True)

  with table_container:
    df = extractFromPlaylist.UrlToDataFrame(url)[0]
    
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    


 

## Sidebar

with st.sidebar:
 messages = st.container(height= 150)
messages.chat_message('user').write(url)
messages.chat_message('assistant').write(f'Echo: {url}')