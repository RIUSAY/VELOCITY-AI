import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# 1. Configuración de Identidad
st.set_page_config(page_title="VELOCITY AI - RADAR GOLD", layout="wide")
st.title("🚀 VELOCITY AI: El Radar de Oro")

# 2. Seguridad de API Key (Secrets o Manual)
try:
    api_key_default = st.secrets["YOUTUBE_API_KEY"]
except:
    api_key_default = ""

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Ajustes de Potencia")
    api_key = st.text_input("API KEY", value=api_key_default, type="password")
    
    st.divider()
    # Volvemos a la búsqueda por palabras clave (Nicho) que es lo más efectivo
    nicho = st.text_input("Nicho / Palabra Clave", value="documentary")
    
    # Selectores simplificados para no bloquear la API
    rango_tiempo = st.selectbox(
        "📅 Antigüedad", 
        ["24 horas", "1 semana", "1 mes", "3 meses", "6 meses", "1 año", "Siempre"],
        index=2
    )
    
    st.divider()
    min_views_req = st.number_input("👁️ Vistas Mínimas", value=20000)
    max_subs_req = st.number_input("📉 Máximo Suscriptores", value=300000)
    ratio_min = st.slider("🔥 Poder Viral (Ratio)", 1.0, 20.0, 3.0)

# --- FUNCIÓN DE FECHA ---
def calcular_fecha(opcion):
    ahora = datetime.utcnow()
    tiempos = {"24 horas": 1, "1 semana": 7, "1 mes": 30, "3 meses": 90, "6 meses": 180, "1 año": 365}
    if opcion == "Siempre": return None
    return (ahora - timedelta(days=tiempos.get(opcion, 30))).strftime('%Y-%m-%dT%H:%M:%SZ')

# --- PROCESO DE ESCANEO ---
if st.button("📡 ACTIVAR RADAR DE HALLAZGOS"):
    if not api_key:
        st.error("Falta API KEY.")
    else:
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            fecha_filtro = calcular_fecha(rango_tiempo)
            
            # BUSQUEDA AGRESIVA: Usamos el método search.list que era el del radar original
            search_params = {
                'q': nicho,
                'part': 'snippet',
                'maxResults': 50,
                'type': 'video',
                'order': 'viewCount',
                'videoEmbeddable': 'true'
            }
            if fecha_filtro:
                search_params['publishedAfter'] = fecha_filtro

            res = youtube.search().list(**search_params).execute()

            v_ids = [i['id']['videoId'] for i in res['items'] if 'videoId' in i['id']]
            
            if not v_ids:
                st.warning("El radar no detectó nada. Intenta cambiar la palabra clave o el tiempo.")
            else:
                # Obtenemos estadísticas reales de los videos encontrados
                v_data = youtube.videos().list(part='statistics,snippet', id=','.join(v_ids)).execute()['items']
                c_ids = [v['snippet']['channelId'] for v in v_data]
                c_stats = {c['id']: c for c in youtube.channels().list(part='statistics', id=','.join(c_ids)).execute()['items']}

                encontrados = 0
                for v in v_data:
                    # Filtro básico anti-música y anti-live
                    if v['snippet'].get('categoryId') == '10' or v['snippet'].get('liveBroadcastContent') != 'none':
                        continue

                    vistas = int(v['statistics'].get('viewCount', 0))
                    c = c_stats.get(v['snippet']['channelId'])
                    
                    if c:
                        subs = int(c['statistics'].get('subscriberCount', 1))
                        ratio = vistas / subs
                        
                        # FILTROS DE CALIDAD (Más flexibles para que salga contenido)
                        if vistas >= min_views_req and subs <= max_subs_req and ratio >= ratio_min:
                            encontrados += 1
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.image(v['snippet']['thumbnails']['high']['url'], use_container_width=True)
                            with col2:
                                st.subheader(v['snippet']['title'])
                                st.write(f"👁️ **VISTAS:** {vistas:,} | 📈 **RATIO:** {round(ratio, 1)}x")
                                st.write(f"📅 Publicado: {v['snippet']['publishedAt'][:10]} | 📺 Canal: {v['snippet']['channelTitle']}")
                                st.link_button("🎥 Analizar Video", f"https://youtube.com/watch?v={v['id']}")
                            st.divider()

                if encontrados == 0:
                    st.info("Radar en línea, pero los filtros son muy estrictos. Baja el 'Ratio' o las 'Vistas Mínimas' para ver resultados.")

        except Exception as e:
            st.error(f"Error de conexión: {e}")
