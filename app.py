import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# 1. IDENTIDAD CORPORATIVA
st.set_page_config(page_title="VELOCITY AI - PROFIT ANALYZER", layout="wide")
st.title("🚀 VELOCITY AI: Profit & Monetization Suite")

try:
    api_key_default = st.secrets["YOUTUBE_API_KEY"]
except:
    api_key_default = ""

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("API KEY", value=api_key_default, type="password")
    st.divider()
    nicho_input = st.text_input("Nicho Maestro", value="curiosidades")
    rango_tiempo = st.selectbox("Antigüedad", ["24 horas", "1 semana", "1 mes", "3 meses", "6 meses", "1 año", "Siempre"], index=5)

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🔍 Radar", "📊 Analizador Video", "🛡️ AUDITORÍA DE GANANCIAS"])

with tab1:
    st.info("Usa el botón de abajo para encontrar nuevos canales.")
    if st.button("📡 ACTIVAR RADAR"):
        # (Lógica del radar mantenida de v6.7...)
        pass

with tab3:
    st.header("🛡️ Auditoría de Canal y Estimación de Ingresos")
    c_input = st.text_input("Pega el ID o @usuario (Ej: @ZkeletonIA)", key="c_profit")
    
    if st.button("Auditar Canal y Monetización"):
        if not api_key:
            st.error("Falta API KEY")
        else:
            try:
                youtube = build('youtube', 'v3', developerKey=api_key)
                handle = c_input.split("/")[-1].replace("@", "")
                
                # Búsqueda del canal
                if c_input.startswith("UC"):
                    c_res = youtube.channels().list(part='snippet,statistics', id=c_input).execute()
                else:
                    c_res = youtube.channels().list(part='snippet,statistics', forHandle=handle).execute()
                
                if c_res.get('items'):
                    det = c_res['items'][0]
                    c_id = det['id']
                    stats = det['statistics']
                    
                    # --- BLOQUE 1: DATOS GENERALES ---
                    col_logo, col_info = st.columns([1, 3])
                    with col_logo:
                        st.image(det['snippet']['thumbnails']['high']['url'], use_container_width=True)
                    with col_info:
                        st.title(det['snippet']['title'])
                        st.write(f"📅 **Se unió:** {det['snippet']['publishedAt'][:10]}")
                        st.write(f"📝 **Descripción:** {det['snippet']['description'][:200]}...")
                    
                    st.divider()
                    
                    # --- BLOQUE 2: MÉTRICAS REALES ---
                    m1, m2, m3 = st.columns(3)
                    vistas_totales = int(stats.get('viewCount', 0))
                    total_videos = int(stats.get('videoCount', 0))
                    m1.metric("Suscriptores", f"{int(stats.get('subscriberCount', 0)):,}")
                    m2.metric("Videos Subidos", total_videos)
                    m3.metric("Visualizaciones Totales", f"{vistas_totales:,}")

                    # --- BLOQUE 3: ESTIMACIÓN DE MONETIZACIÓN (LÓGICA CEO) ---
                    st.subheader("💰 Análisis de Monetización Estimada")
                    # Un canal de curiosidades suele tener un CPM de entre $1.5 y $4.0 USD
                    cpm_min, cpm_max = 1.5, 4.0
                    ganancia_total_min = (vistas_totales / 1000) * cpm_min
                    ganancia_total_max = (vistas_totales / 1000) * cpm_max
                    
                    c_mon1, c_mon2 = st.columns(2)
                    with c_mon1:
                        st.success(f"**Ganancia Histórica Est.:** ${ganancia_total_min:,.2f} - ${ganancia_total_max:,.2f} USD")
                    with c_mon2:
                        # Estimación mensual basada en promedio de vistas por video
                        vistas_promedio = vistas_totales / total_videos if total_videos > 0 else 0
                        st.info(f"**Valor Promedio por Video:** ${ (vistas_promedio/1000)*cpm_min:,.2f} USD")
                    
                    st.write("⚠️ *Nota: La monetización depende del país de la audiencia y si el contenido es apto para anunciantes.*")

                    # --- BLOQUE 4: VIDEOS MÁS VIRALES CON MINIATURAS ---
                    st.divider()
                    st.subheader("🔥 Top Videos Virales (Análisis Visual)")
                    v_list = youtube.search().list(channelId=c_id, part='snippet', order='viewCount', maxResults=6, type='video').execute()
                    
                    cols = st.columns(3) # Galería de 3 columnas
                    for idx, vid in enumerate(v_list.get('items', [])):
                        with cols[idx % 3]:
                            st.image(vid['snippet']['thumbnails']['high']['url'], use_container_width=True)
                            st.caption(vid['snippet']['title'])
                            st.write(f"🔗 [Link al Video](https://youtube.com/watch?v={vid['id']['videoId']})")
                else:
                    st.error("Canal no encontrado.")
            except Exception as e:
                st.error(f"Error en Auditoría: {e}")
