import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Configuración de Identidad
st.set_page_config(page_title="VELOCITY AI - GLOBAL HUNTER", layout="wide")
st.title("🚀 VELOCITY AI: Global Faceless Intelligence")

# Seguridad de API Key
try:
    api_key_default = st.secrets["YOUTUBE_API_KEY"]
except:
    api_key_default = ""

# --- BARRA LATERAL: FILTROS DE ÉLITE ---
with st.sidebar:
    st.header("⚙️ Ajustes de Cacería")
    api_key = st.text_input("API KEY", value=api_key_default, type="password")
    
    st.divider()
    
    # Selector de Idioma (Mercado)
    idioma = st.selectbox("🌎 Idioma del Video", ["Inglés (en)", "Español (es)"], index=0)
    lang_code = "en" if "Inglés" in idioma else "es"
    
    # Selector de Tiempo (Rango de Publicación solicitado)
    rango_tiempo = st.selectbox(
        "📅 Antigüedad del Video", 
        ["1 año", "8 meses", "6 meses", "3 meses", "1 mes", "1 semana", "24 horas"],
        index=3
    )
    
    # Filtros de Métricas
    ratio_min = st.slider("🔥 Poder Viral Mínimo (Ratio)", 5, 100, 10)
    max_subs = st.number_input("📉 Máximo de Suscriptores", value=250000)
    min_views = st.number_input("👁️ Mínimo de Vistas", value=50000)

# --- FUNCIÓN PARA CALCULAR LA FECHA ---
def calcular_fecha_publicacion(opcion):
    ahora = datetime.utcnow()
    tiempos = {
        "1 año": 365, "8 meses": 240, "6 meses": 180, 
        "3 meses": 90, "1 mes": 30, "1 semana": 7, "24 horas": 1
    }
    dias = tiempos.get(opcion, 30)
    return (ahora - timedelta(days=dias)).strftime('%Y-%m-%dT%H:%M:%SZ')

# --- PROCESO DE ESCANEO ---
if st.button("📡 INICIAR BÚSQUEDA DE ALTO RENDIMIENTO"):
    if not api_key:
        st.error("⚠️ Falta API KEY.")
    else:
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            fecha_filtro = calcular_fecha_publicacion(rango_tiempo)
            
            # Buscamos videos con filtros específicos
            res = youtube.search().list(
                part='snippet',
                maxResults=50,
                order='viewCount',
                type='video',
                relevanceLanguage=lang_code,
                publishedAfter=fecha_filtro,
                videoEmbeddable='true',
                videoDefinition='high',
                eventType='completed' if rango_tiempo != "24 horas" else 'none'
            ).execute()

            v_ids = [i['id']['videoId'] for i in res['items']]
            
            if not v_ids:
                st.warning("No se encontraron videos iniciales. Prueba con otro rango de tiempo.")
            else:
                # Obtener datos extendidos
                v_data = youtube.videos().list(part='statistics,snippet', id=','.join(v_ids)).execute()['items']
                c_ids = [v['snippet']['channelId'] for v in v_data]
                c_data = youtube.channels().list(part='statistics', id=','.join(c_ids)).execute()['items']
                c_stats = {c['id']: c for c in c_data}

                anomalias = []
                for v in v_data:
                    # 1. EVITAR MÚSICA (Categoría 10)
                    if v['snippet'].get('categoryId') == '10':
                        continue
                    
                    # 2. EVITAR LIVES (Solo contenido grabado)
                    if v['snippet'].get('liveBroadcastContent') != 'none':
                        continue

                    v
