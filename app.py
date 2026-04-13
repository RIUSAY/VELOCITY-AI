import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# 1. IDENTIDAD CORPORATIVA
st.set_page_config(page_title="VELOCITY AI - BUSINESS INTEL", layout="wide")
st.title("🚀 VELOCITY AI: Global Intelligence Suite")

# 2. SEGURIDAD DE DATOS (API KEY)
try:
    api_key_default = st.secrets["YOUTUBE_API_KEY"]
except:
    api_key_default = ""

# --- BARRA LATERAL: AJUSTES ESTRATÉGICOS ---
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
    st.info("Configuración optimizada para detección de canales Faceless.")

# --- FUNCIONES TÉCNICAS ---
def calcular_fecha(opcion):
    ahora = datetime.utcnow()
    tiempos = {"24 horas": 1, "1 semana": 7, "1 mes": 30, "3 meses": 90, "6 meses": 180, "1 año": 365}
    if opcion == "Siempre": return None
    return (ahora - timedelta(days=tiempos.get(opcion, 30))).strftime('%Y-%m-%dT%H:%M:%SZ')

# --- DEFINICIÓN DE PESTAÑAS (CRÍTICO) ---
tab1, tab2, tab3 = st.tabs(["🔍 Radar de Volumen", "📊 Analizador de Video", "🛡️ Auditor de Canal"])

# --- PESTAÑA 1: RADAR ---
with tab1:
    if st.button("📡 LANZAR ESCANEO (+50 RESULTADOS)"):
        if not api_key: st.error("Falta API KEY")
        else:
            try:
                youtube = build('youtube', 'v3', developerKey=api_key)
                fecha = calcular_fecha(rango_tiempo)
                res = youtube.search().list(q=nicho_input, part='snippet', maxResults=50, type='video', order='viewCount', publishedAfter=fecha if fecha else None).execute()
                
                encontrados = 0
                for item in res.get('items', []):
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
                if encontrados == 0: st.warning("No hubo coincidencias. Ajusta los filtros.")
            except Exception as e: st.error(f"Error: {e}")

# --- PESTAÑA 2: ANALIZADOR ---
with tab2:
    st.header("🔬 Inteligencia de Video")
    v_input = st.text_input("ID o URL del Video")
    if st.button("Analizar"):
        try:
            v_id_clean = v_input.split("v=")[-1] if "v=" in v_input else v_input
            youtube = build('youtube', 'v3', developerKey=api_key)
            v_det = youtube.videos().list(part='snippet,statistics', id=v_id_clean).execute()
            if v_det['items']:
                item = v_det['items'][0]
                st.image(item['snippet']['thumbnails']['high']['url'], width=400)
                st.write(f"**Etiquetas:** {',
