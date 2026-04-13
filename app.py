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
    st.info("Sistema optimizado para canales Faceless de alto rendimiento.")

# --- FUNCIONES TÉCNICAS ---
def calcular_fecha(opcion):
    ahora = datetime.utcnow()
    tiempos = {"24 horas": 1, "1 semana": 7, "1 mes": 30, "3 meses": 90, "6 meses": 180, "1 año": 365}
    if opcion == "Siempre": return None
    return (ahora - timedelta(days=tiempos.get(opcion, 30))).strftime('%Y-%m-%dT%H:%M:%SZ')

# --- DEFINICIÓN DE PESTAÑAS ---
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
                if encontrados == 0: st.warning("No hubo coincidencias exactas. Prueba bajando las vistas mínimas.")
            except Exception as e: st.error(f"Error en Radar: {e}")

# --- PESTAÑA 2: ANALIZADOR ---
with tab2:
    st.header("🔬 Inteligencia de Video")
    v_input = st.text_input("ID o URL del Video", key="analizador_input")
    if st.button("Analizar Video"):
        if not api_key: st.error("Falta API KEY")
        else:
            try:
                v_id_clean = v_input.split("v=")[-1] if "v=" in v_input else v_input
                v_id_clean = v_id_clean.split("&")[0] # Limpiar parámetros extras
                youtube = build('youtube', 'v3', developerKey=api_key)
                v_det = youtube.videos().list(part='snippet,statistics', id=v_id_clean).execute()
                if v_det['items']:
                    item = v_det['items'][0]
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        st.image(item['snippet']['thumbnails']['high']['url'], use_container_width=True)
                    with col_b:
                        st.subheader(item['snippet']['title'])
                        tags = item['snippet'].get('tags', [])
                        st.write(f"**Etiquetas:** {', '.join(tags) if tags else 'Sin etiquetas'}")
                        st.metric("Vistas Totales", f"{int(item['statistics'].get('viewCount', 0)):,}")
                        st.write(f"📅 **Publicado:** {item['snippet']['publishedAt'][:10]}")
                else: st.error("No se encontró el video. Verifica el ID.")
            except Exception as e: st.error(f"Error en Analizador: {e}")

# --- PESTAÑA 3: AUDITOR ---
with tab3:
    st.header("🛡️ Auditoría de Canal")
    c_input = st.text_input("ID o URL del Canal (@usuario o UC...)", key="auditor_input")
    if st.button("Auditar Canal"):
        if not api_key: st.error("Falta API KEY")
        else:
            try:
                youtube = build('youtube', 'v3', developerKey=api_key)
                cid = c_input.split("/")[-1].replace("@", "")
                
                # Intentar por Handle (nombre con @) o por ID de canal (UC...)
                if c_input.startswith("UC") or "channel/UC" in c_input:
                    clean_id = c_input.split("/")[-1]
                    c_res = youtube.channels().list(part='snippet,statistics', id=clean_id).execute()
                else:
                    c_res = youtube.channels().list(part='snippet,statistics', forHandle=cid).execute()
                
                if c_res.get('items'):
                    det = c_res['items'][0]
                    st.title(det['snippet']['title'])
                    st.image(det['snippet']['thumbnails']['high']['url'], width=150)
                    st.metric("Suscriptores", f"{int(det['statistics'].get('subscriberCount', 0)):,}")
                    st.write(f"**Descripción:** {det['snippet']['description'][:400]}...")
                else: st.error("Canal no encontrado. Intenta pegando el ID completo
