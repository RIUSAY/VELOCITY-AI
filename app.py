import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# 1. Configuración de Identidad
st.set_page_config(page_title="VELOCITY AI - MASSIVE TRAFFIC", layout="wide")
st.title("🚀 VELOCITY AI: Massive Global Traffic")

# 2. Seguridad de API Key
try:
    api_key_default = st.secrets["YOUTUBE_API_KEY"]
except:
    api_key_default = ""

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Ajustes de Tráfico")
    api_key = st.text_input("API KEY", value=api_key_default, type="password")
    
    st.divider()
    idioma = st.selectbox("🌎 Idioma", ["Inglés (en)", "Español (es)"], index=0)
    lang_code = "en" if "Inglés" in idioma else "es"
    
    rango_tiempo = st.selectbox(
        "📅 Antigüedad", 
        ["1 año", "8 meses", "6 meses", "3 meses", "1 mes", "1 semana", "24 horas"],
        index=3
    )
    
    # Bajamos la exigencia del Ratio para que muestre MÁS resultados
    ratio_min_req = st.slider("Poder Viral Mínimo (Flexible)", 1.0, 50.0, 2.0)
    min_views_req = st.number_input("👁️ Vistas Mínimas (Prioridad)", value=100000)
    max_subs_req = st.number_input("📉 Máximo Suscriptores", value=1000000)

def calcular_fecha(opcion):
    ahora = datetime.utcnow()
    tiempos = {"1 año": 365, "8 meses": 240, "6 meses": 180, "3 meses": 90, "1 mes": 30, "1 semana": 7, "24 horas": 1}
    return (ahora - timedelta(days=tiempos.get(opcion, 30))).strftime('%Y-%m-%dT%H:%M:%SZ')

# --- PROCESO DE ESCANEO ---
if st.button("📡 LANZAR ESCANEO DE TRÁFICO MASIVO"):
    if not api_key:
        st.error("Falta API KEY.")
    else:
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            fecha_filtro = calcular_fecha(rango_tiempo)
            
            # Buscamos los 50 videos con más vistas de ese idioma y periodo
            res = youtube.search().list(
                part='snippet',
                maxResults=50,
                order='viewCount',
                type='video',
                relevanceLanguage=lang_code,
                publishedAfter=fecha_filtro
            ).execute()

            v_ids = [i['id']['videoId'] for i in res['items'] if 'videoId' in i['id']]
            
            if not v_ids:
                st.warning("No se encontraron videos. Prueba un rango de tiempo más amplio.")
            else:
                v_data = youtube.videos().list(part='statistics,snippet', id=','.join(v_ids)).execute()['items']
                c_ids = [v['snippet']['channelId'] for v in v_data]
                c_stats = {c['id']: c for c in youtube.channels().list(part='statistics', id=','.join(c_ids)).execute()['items']}

                encontrados = 0
                for v in v_data:
                    # Filtros básicos obligatorios (No música, No lives)
                    if v['snippet'].get('categoryId') == '10' or v['snippet'].get('liveBroadcastContent') != 'none':
                        continue

                    vistas = int(v['statistics'].get('viewCount', 0))
                    c = c_stats.get(v['snippet']['channelId'])
                    
                    if c:
                        subs = int(c['statistics'].get('subscriberCount', 1))
                        ratio = vistas / subs
                        
                        # PRIORIDAD: Que tenga muchas vistas, el ratio es secundario
                        if vistas >= min_views_req and subs <= max_subs_req:
                            encontrados += 1
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.image(v['snippet']['thumbnails']['high']['url'], use_container_width=True)
                            with col2:
                                st.subheader(v['snippet']['title'])
                                st.write(f"👁️ **VISTAS:** {vistas:,}")
                                st.write(f"📅 Publicado: {v['snippet']['publishedAt'][:10]} | 📈 Ratio: {round(ratio, 1)}x")
                                st.write(f"📺 Canal: {v['snippet']['channelTitle']} ({subs:,} subs)")
                                st.link_button("🎥 Analizar este éxito", f"https://youtube.com/watch?v={v['id']}")
                            st.divider()

                if encontrados == 0:
                    st.info("No hay videos que cumplan los filtros. He bajado la exigencia, prueba pulsar el botón de nuevo.")

        except Exception as e:
            st.error(f"Error: {e}")
