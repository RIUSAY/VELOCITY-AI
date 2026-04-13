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
    
    # Selector de Tiempo (Rango de Publicación)
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
            
            # Buscamos videos más populares con filtros específicos
            # Excluimos 'música' (categoría 10) mediante la lógica de filtrado posterior
            res = youtube.search().list(
                part='snippet',
                maxResults=50,
                order='viewCount',
                type='video',
                relevanceLanguage=lang_code,
                publishedAfter=fecha_filtro,
                videoEmbeddable='true',
                videoDefinition='high',
                # videoEventType='none' evita los 'Live' actuales
                eventType='completed' if rango_tiempo != "24 horas" else 'none'
            ).execute()

            v_ids = [i['id']['videoId'] for i in res['items']]
            
            # Obtener datos extendidos de videos y canales
            v_data = youtube.videos().list(part='statistics,snippet,topicDetails', id=','.join(v_ids)).execute()['items']
            c_ids = [v['snippet']['channelId'] for v in v_data]
            c_data = youtube.channels().list(part='statistics', id=','.join(c_ids)).execute()['items']
            c_stats = {c['id']: c for c in c_data}

            anomalias = []
            for v in v_data:
                # 1. EVITAR MÚSICA: Filtrar por CategoryId (10 es música)
                if v['snippet'].get('categoryId') == '10':
                    continue
                
                # 2. EVITAR LIVES: Solo videos que no sean transmisiones en vivo
                if v['snippet'].get('liveBroadcastContent') != 'none':
                    continue

                vistas = int(v['statistics'].get('viewCount', 0))
                c = c_stats.get(v['snippet']['channelId'])
                
                if c:
                    subs = int(c['statistics'].get('subscriberCount', 1))
                    ratio = vistas / subs
                    
                    # 3. FILTRO DE PODER Y SUBSCRIPTORES
                    if ratio >= ratio_min and subs <= max_subs and vistas >= min_views:
                        anomalias.append({
                            "Thumb": v['snippet']['thumbnails']['high']['url'],
                            "Título": v['snippet']['title'],
                            "Canal": v['snippet']['channelTitle'],
                            "Publicado": v['snippet']['publishedAt'][:10],
                            "Ratio": f"{round(ratio, 1)}x",
                            "Vistas": vistas,
                            "Subs": subs,
                            "Link": f"https://youtube.com/watch?v={v['id']}"
                        })

            if anomalias:
                st.success(f"🎯 ¡Radar Limpio! Encontradas {len(anomalias)} minas de oro faceless.")
                for item in anomalias:
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(item['Thumb'], use_container_width=True)
                    with col2:
                        st.subheader(item['Título'])
                        st.write(f"📅 **Publicado:** {item['Publicado']} | 📈 **Ratio:** {item['Ratio']}")
                        st.write(f"👀 **Vistas:** {item['Vistas']:,} | 📺 **Canal:** {item['Canal']} ({item['Subs']:,} subs)")
                        st.link_button("🎥 Ver Estrategia", item['Link'])
                    st.divider()
            else:
                st.warning("No hay videos que cumplan estos criterios tan estrictos ahora. Intenta bajar el Ratio.")

        except Exception as e:
            st.error(f"Error de CEO: {e}")
                st.warning("No hay videos que rompan el algoritmo en este momento. Intenta bajar el Ratio.")
                
        except Exception as e:
            st.error(f"Error técnico: {e}")
