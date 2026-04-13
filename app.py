import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE IDENTIDAD
st.set_page_config(page_title="VELOCITY AI - BUSINESS INTEL", layout="wide")
st.title("🚀 VELOCITY AI: Global Intelligence Suite")

# 2. SEGURIDAD DE API KEY
try:
    api_key_default = st.secrets["YOUTUBE_API_KEY"]
except:
    api_key_default = ""

# --- BARRA LATERAL: AJUSTES ---
with st.sidebar:
    st.header("⚙️ Centro de Control")
    api_key = st.text_input("API KEY", value=api_key_default, type="password")
    st.divider()
    nicho_input = st.text_input("Nicho Maestro", value="documentary")
    rango_tiempo = st.selectbox(
        "📅 Antigüedad Máxima", 
        ["24 horas", "1 semana", "1 mes", "3 meses", "6 meses", "1 año", "Siempre"],
        index=2
    )
    st.divider()
    min_views_req = st.number_input("👁️ Vistas Mínimas", value=30000)
    max_subs_req = st.number_input("📉 Máximo Suscriptores", value=400000)

# --- FUNCIONES TÉCNICAS ---
def calcular_fecha(opcion):
    ahora = datetime.utcnow()
    tiempos = {"24 horas": 1, "1 semana": 7, "1 mes": 30, "3 meses": 90, "6 meses": 180, "1 año": 365}
    if opcion == "Siempre": return None
    return (ahora - timedelta(days=tiempos.get(opcion, 30))).strftime('%Y-%m-%dT%H:%M:%SZ')

# --- DEFINICIÓN DE PESTAÑAS (CRÍTICO: ORDEN CORRECTO) ---
tab1, tab2, tab3 = st.tabs(["🔍 Radar de Volumen", "📊 Analizador de Video", "🛡️ Auditor de Canal"])

# --- PESTAÑA 1: RADAR ---
with tab1:
    if st.button("📡 LANZAR ESCANEO (+50)"):
        if not api_key: st.error("Falta API KEY")
        else:
            try:
                youtube = build('youtube', 'v3', developerKey=api_key)
                fecha = calcular_fecha(rango_tiempo)
                res = youtube.search().list(q=nicho_input, part='snippet', maxResults=50, type='video', order='viewCount', publishedAfter=fecha if fecha else None).execute()
                
                encontrados = 0
                for item in res.get('items', []):
                    if 'videoId' not in item['id']: continue
                    v_id = item['id']['videoId']
                    v_res = youtube.videos().list(part='statistics,snippet', id=v_id).execute()
                    if not v_res['items']: continue
                    
                    v_info = v_res['items'][0]
                    c_id = v_info['snippet']['channelId']
                    c_res = youtube.channels().list(part='statistics', id=c_id).execute()
                    if not c_res['items']: continue
                    
                    vistas = int(v_info['statistics'].get('viewCount', 0))
                    subs = int(c_res['items'][0]['statistics'].get('subscriberCount', 1))
                    
                    if vistas >= min_views_req and subs <= max_subs_req:
                        encontrados += 1
                        c1, c2 = st.columns([1, 2])
                        with c1: st.image(v_info['snippet']['thumbnails']['high']['url'])
                        with c2:
                            st.subheader(v_info['snippet']['title'])
                            st.write(f"👁️ **Vistas:** {vistas:,} | 📈 **Ratio:** {round(vistas/subs, 1)}x")
                            st.write(f"🆔 Video: `{v_id}` | 🆔 Canal: `{c_id}`")
                            st.link_button("🎥 Ver Video", f"https://youtube.com/watch?v={v_id}")
                        st.divider()
            except Exception as e: st.error(f"Error: {e}")

# --- PESTAÑA 2: ANALIZADOR ---
with tab2:
    st.header("🔬 Inteligencia de Video")
    v_input = st.text_input("ID o URL del Video", key="v_analisis")
    if st.button("Analizar Video"):
        try:
            v_id_clean = v_input.split("v=")[-1].split("&")[0] if "v=" in v_input else v_input
            youtube = build('youtube', 'v3', developerKey=api_key)
            v_res = youtube.videos().list(part='snippet,statistics', id=v_id_clean).execute()
            if v_res.get('items'):
                item = v_res['items'][0]
                st.image(item['snippet']['thumbnails']['high']['url'], width=400)
                st.subheader(item['snippet']['title'])
                st.metric("Vistas Totales", f"{int(item['statistics'].get('viewCount', 0)):,}")
            else: st.error("Video no encontrado.")
        except Exception as e: st.error(f"Error: {e}")

# --- PESTAÑA 3: AUDITOR ---
with tab3:
    st.header("🛡️ Auditoría de Canal")
    c_input = st.text_input("ID o @usuario (Ej: @ZkeletonIA)", key="c_auditor")
    if st.button("Auditar Canal"):
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            cid = c_input.split("/")[-1].replace("@", "")
            
            if cid.startswith("UC"):
                c_res = youtube.channels().list(part='snippet,statistics', id=cid).execute()
            else:
                c_res = youtube.channels().list(part='snippet,statistics', forHandle=cid).execute()
            
            if c_res.get('items'):
                det = c_res['items'][0]
                c_id_real = det['id']
                col_a, col_b = st.columns([1, 3])
                with col_a: st.image(det['snippet']['thumbnails']['high']['url'], use_container_width=True)
                with col_b:
                    st.title(det['snippet']['title'])
                    st.write(f"📅 **Se unió:** {det['snippet']['publishedAt'][:10]}")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Suscriptores", f"{int(det['statistics'].get('subscriberCount', 0)):,}")
                    m2.metric("Videos", det['statistics'].get('videoCount'))
                    m3.metric("Vistas Totales", f"{int(det['statistics'].get('viewCount', 0)):,}")
                
                st.divider()
                st.subheader("🔥 Top Videos Virales")
                v_list = youtube.search().list(channelId=c_id_real, part='snippet', order='viewCount', maxResults=6, type='video').execute()
                cols = st.columns(3)
                for idx, vid in enumerate(v_list.get('items', [])):
                    with cols[idx % 3]:
                        st.image(vid['snippet']['thumbnails']['high']['url'], use_container_width=True)
                        st.caption(vid['snippet']['title'][:50])
                        st.write(f"🔗 [Link](https://youtube.com/watch?v={vid['id']['videoId']})")
            else: st.error("Canal no encontrado.")
        except Exception as e: st.error(f"Error en Auditoría: {e}")
