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
try:
  params= st.query_params
  if params:
    st.title(f"Détails pour la playlist de CrashCourse : {params['name']}")
    # st.title(params.playlist)

    # extract_videos_from_playlists.PlaylistToVideos(params['playlist'])
    url =  params.get("playlist", "")
    print(url)
    df = extractFromPlaylist.UrlToDataFrame(url)
    image = extractFromPlaylist.miniatureFromPlaylist(url)
    description_playlist = extractFromPlaylist.getDescriptionFromPlaylist(url)
    sources = f'<a href="{extractFromPlaylist.cleanDescriptions(url)["gdocs_links"]}" target=_blank> Sources</a>'
    # description de la playlist  pour la mettre dans une carte (metric)
    
    description_container = st.container(
      border = True
      
    )
    table_container = st.container(
      horizontal= True
    )
    with description_container:
      
      st.markdown(
    f'<img src="{image}">', unsafe_allow_html=True)
      st.write(description_playlist)
      
      st.write(sources, unsafe_allow_html=True)
    
    with table_container:
      df = extractFromPlaylist.UrlToDataFrame(url)
      
      st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

except: # Point de départ : playlist envoyée manuellement
  if url := st.chat_input('URL de la playlist à analyser: '):
    messages = st.container(height= 100)
    messages.chat_message('user').write(url)
  
  df = extractFromPlaylist.UrlToDataFrame(url)
  image = extractFromPlaylist.miniatureFromPlaylist(url)
  description_playlist = extractFromPlaylist.getDescriptionFromPlaylist(url)
  sources = f'<a href="{extractFromPlaylist.cleanDescriptions(url)["gdocs_links"]}" target=_blank> Sources</a>'
  # description de la playlist  pour la mettre dans une carte (metric)
  
  description_container = st.container(
    border = True
    
  )
  table_container = st.container(
    horizontal= True
  )
  with description_container:
    
    st.markdown(
  f'<img src="{image}">', unsafe_allow_html=True)
    st.write(description_playlist)
    
    st.write(sources, unsafe_allow_html=True)
  
  with table_container:
    df = extractFromPlaylist.UrlToDataFrame(url)
    
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    
 
 

## Sidebar

with st.sidebar:
 messages = st.container(height= 150)
 if url := st.chat_input("Say Something"):
  messages.chat_message('user').write(url)
  messages.chat_message('assistant').write(f'Echo: {url}')