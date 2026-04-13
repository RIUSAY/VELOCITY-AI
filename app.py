import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# 1. Configuración de Identidad
st.set_page_config(page_title="VELOCITY AI - BUSINESS INTEL", layout="wide")
st.title("🚀 VELOCITY AI: Intelligence & Audit Suite")

# 2. Seguridad de API Key
try:
    api_key_default = st.secrets["YOUTUBE_API_KEY"]
except:
    api_key_default = ""

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Panel de Control")
    api_key = st.text_input("API KEY", value=api_key_default, type="password")
    st.divider()
    nicho = st.text_input("Nicho de Cacería", value="mystery")
    rango_tiempo = st.selectbox("Antigüedad", ["24 horas", "1 semana", "1 mes", "3 meses", "6 meses", "1 año", "Siempre"], index=2)
    st.divider()
    max_subs_req = st.number_input("Límite de Suscriptores", value=500000)
    min_views_req = st.number_input("Vistas Mínimas", value=50000)

# --- FUNCIONES TÉCNICAS ---
def calcular_fecha(opcion):
    ahora = datetime.utcnow()
    tiempos = {"24 horas": 1, "1 semana": 7, "1 mes": 30, "3 meses": 90, "6 meses": 180, "1 año": 365}
    if opcion == "Siempre": return None
    return (ahora - timedelta(days=tiempos.get(opcion, 30))).strftime('%Y-%m-%dT%H:%M:%SZ')

# --- INTERFAZ DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🔍 Radar de Virales", "📊 Analizador de Video", "🛡️ Auditor de Canal"])

with tab1:
    if st.button("📡 ACTIVAR RADAR"):
        if not api_key: st.error("Falta API KEY")
        else:
            try:
                youtube = build('youtube', 'v3', developerKey=api_key)
                fecha = calcular_fecha(rango_tiempo)
                res = youtube.search().list(q=nicho, part='snippet', maxResults=20, type='video', order='viewCount', publishedAfter=fecha if fecha else None).execute()
                
                for item in res['items']:
                    v_id = item['id']['videoId']
                    v_res = youtube.videos().list(part='statistics,snippet', id=v_id).execute()
                    if not v_res['items']: continue
                    
                    v_info = v_res['items'][0]
                    c_id = v_info['snippet']['channelId']
                    c_res = youtube.channels().list(part='statistics', id=c_id).execute()
                    if not c_res['items']: continue
                    
                    c_info = c_res['items'][0]
                    vistas = int(v_info['statistics'].get('viewCount', 0))
                    subs = int(c_info['statistics'].get('subscriberCount', 1))
                    ratio = vistas / subs

                    if vistas >= min_views_req and subs <= max_subs_req:
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.image(v_info['snippet']['thumbnails']['high']['url'])
                        with col2:
                            st.subheader(v_info['snippet']['title'])
                            st.write(f"📈 **Ratio:** {round(ratio,1)}x | 👀 **Vistas:** {vistas:,}")
                            st.write(f"🆔 **ID Video:** `{v_id}`")
                            st.write(f"🆔 **ID Canal:** `{c_id}`")
                            st.link_button("🎥 Ver Video", f"https://youtube.com/watch?v={v_id}")
                        st.divider()
            except Exception as e:
                st.error(f"Error en Radar: {e}")

with tab2:
    st.header("🔬 Análisis Profundo de Video")
    video_input = st.text_input("Pega el ID del Video o la URL", key="v_input")
    if st.button("Analizar Video"):
        v_id = video_input.split("v=")[-1] if "v=" in video_input else video_input
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            v_res = youtube.videos().list(part='snippet,statistics', id=v_id).execute()
            if v_res['items']:
                v_det = v_res['items'][0]
                c1, c2 = st.columns(2)
                with c1:
                    st.image(v_det['snippet']['thumbnails']['high']['url'])
                    st.write(f"**Tags:** {', '.join(v_det['snippet'].get('tags', ['No tiene']))}")
                with c2:
                    st.metric("Vistas Totales", f"{int(v_det['statistics'].get('viewCount', 0)):,}")
                    st.metric("Likes", f"{int(v_det['statistics'].get('likeCount', 0)):,}")
                    st.write(f"**Publicado:** {v_det['snippet']['publishedAt'][:10]}")
            else:
                st.warning("No se encontró información para ese ID de video.")
        except Exception as e:
            st.error(f"Error en Analizador: {e}")

with tab3:
    st.header("🛡️ Auditoría de Canal")
    canal_input = st.text_input("Pega el ID del Canal", key="c_input")
    if st.button("Auditar Canal"):
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            c_res = youtube.channels().list(part='snippet,statistics', id=canal_input).execute()
            
            if c_res['items']:
                c_det = c_res['items'][0]
                col_a, col_b = st.columns([1, 3])
                with col_a:
                    st.image(c_det['snippet']['thumbnails']['high']['url'])
                with col_b:
                    st.title(c_det['snippet']['title'])
                    st.metric("Suscriptores", f"{int(c_det['statistics'].get('subscriberCount', 0)):,}")
                    st.metric("Total Videos", c_det['statistics'].get('videoCount', 0))
                
                st.write("---")
                st.subheader("🔝 Top Videos Recientes")
                v_list = youtube.search().list(channelId=canal_input, part='snippet', order='viewCount', maxResults=5, type='video').execute()
                for vid in v_list.get('items', []):
                    st.write(f"▶️ **{vid['snippet']['title']}** (ID: `{vid['id']['videoId']}`)")
            else:
                st.warning("Canal no encontrado. Verifica que el ID sea correcto (Ej: UCxxxxxx).")
        except Exception as e:
            st.error(f"Error en Auditoría: {e}")
