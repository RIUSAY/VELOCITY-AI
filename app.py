import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

st.set_page_config(page_title="VELOCITY AI - GLOBAL", layout="wide")
st.title("🚀 VELOCITY AI: Global Faceless Hunter")

# --- SEGURIDAD Y CLAVE ---
try:
    api_key_default = st.secrets["YOUTUBE_API_KEY"]
except:
    api_key_default = ""

with st.sidebar:
    st.header("⚙️ Radar Global")
    api_key = st.text_input("API KEY", value=api_key_default, type="password")
    
    # Filtros de potencia
    ratio_min = st.slider("Poder Viral Mínimo (x veces)", 5, 100, 10)
    max_subs = st.number_input("Límite de Suscriptores", value=250000)
    
    st.divider()
    st.write("🌍 Configurado para: **Mercado Global (USA)**")
    st.write("📊 Objetivo: **Canales Faceless Explosivos**")

# --- MOTOR DE BÚSQUEDA GLOBAL ---
if st.button("📡 INICIAR ESCANEO GLOBAL DE VIRALES"):
    if not api_key:
        st.error("Configura la API KEY en Secrets o el panel.")
    else:
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Buscamos los videos más populares del momento sin restricción de nicho
            # Enfocado en USA para capturar tendencias que luego se replican en el mundo
            res = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                chart='mostPopular',
                regionCode='US',
                maxResults=50
            ).execute()

            v_ids = [i['id'] for i in res['items']]
            c_ids = list(set([i['snippet']['channelId'] for i in res['items']]))
            
            # Obtenemos stats de los canales para filtrar por tamaño
            c_stats = {c['id']: c for c in youtube.channels().list(part='statistics', id=','.join(c_ids)).execute()['items']}

            anomalias = []
            for v in res['items']:
                c = c_stats.get(v['snippet']['channelId'])
                if c:
                    vistas = int(v['statistics'].get('viewCount', 0))
                    subs = int(c['statistics'].get('subscriberCount', 1))
                    ratio = vistas / subs
                    
                    # FILTRO DE ORO: 
                    # 1. El ratio debe ser masivo (Poder Viral)
                    # 2. Canal pequeño o mediano (Faceless detectado)
                    if ratio >= ratio_min and subs <= max_subs:
                        anomalias.append({
                            "Thumb": v['snippet']['thumbnails']['high']['url'],
                            "Título": v['snippet']['title'],
                            "Canal": v['snippet']['channelTitle'],
                            "Ratio": f"{round(ratio, 1)}x",
                            "Vistas": f"{vistas:,}",
                            "Subs": f"{subs:,}",
                            "Link": f"https://youtube.com/watch?v={v['id']}"
                        })

            if anomalias:
                st.success(f"¡Radar activo! Detectadas {len(anomalias)} anomalías globales.")
                
                for item in anomalias:
                    col_img, col_txt = st.columns([1, 2])
                    with col_img:
                        st.image(item['Thumb'], use_container_width=True)
                    with col_txt:
                        st.subheader(item['Título'])
                        st.write(f"📈 **PODER VIRAL: {item['Ratio']}**")
                        st.write(f"📺 Canal: {item['Canal']} | 👀 Vistas: {item['Vistas']}")
                        st.link_button("🎥 Analizar Video", item['Link'])
                    st.divider()
            else:
                st.warning("No hay videos que rompan el algoritmo en este momento. Intenta bajar el Ratio.")
                
        except Exception as e:
            st.error(f"Error técnico: {e}")
