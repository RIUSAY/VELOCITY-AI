import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Configuración de Identidad y Estilo Visual
st.set_page_config(page_title="VELOCITY AI - VISUAL INTEL", layout="wide")
st.title("🚀 VELOCITY AI: Visual Market Intelligence")

# Inicializar Base de Datos en la sesión
if 'database' not in st.session_state:
    st.session_state['database'] = pd.DataFrame(columns=["Fecha", "Miniatura", "Título", "Canal", "Vistas", "Ratio", "Link"])

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("YouTube API KEY", type="password")
    nicho_input = st.text_input("Nicho Maestro", value="mystery documentary")
    tiempo = st.selectbox("Publicado en:", ["Últimas 24h", "Última semana", "Último mes"], index=1)
    idioma = st.selectbox("Mercado", ["en", "es"])
    max_subs = st.number_input("Máximo Suscriptores", value=200000)

# --- FUNCIÓN DE TIEMPO ---
def obtener_fecha(opcion):
    ahora = datetime.utcnow()
    dias = {"Últimas 24h": 1, "Última semana": 7, "Último mes": 30}
    return (ahora - timedelta(days=dias.get(opcion, 7))).strftime('%Y-%m-%dT%H:%M:%SZ')

# --- PANEL PRINCIPAL ---
tab1, tab2 = st.tabs(["🔍 Radar Visual", "📂 Biblioteca de Éxitos"])

with tab1:
    if st.button("🔥 INICIAR ESCANEO VISUAL"):
        if not api_key:
            st.error("Falta API KEY")
        else:
            try:
                youtube = build('youtube', 'v3', developerKey=api_key)
                res = youtube.search().list(
                    q=nicho_input, part='snippet', maxResults=30, type='video',
                    order='viewCount', publishedAfter=obtener_fecha(tiempo),
                    regionCode='US' if idioma=='en' else 'MX'
                ).execute()
                
                v_ids = [i['id']['videoId'] for i in res['items']]
                v_data = youtube.videos().list(part='statistics,snippet', id=','.join(v_ids)).execute()['items']
                v_stats = {v['id']: v for v in v_data}
                c_ids = list(set([i['snippet']['channelId'] for i in res['items']]))
                c_stats = {c['id']: c for c in youtube.channels().list(part='statistics', id=','.join(c_ids)).execute()['items']}

                st.write("### 💎 Oportunidades Detectadas")
                
                for i in res['items']:
                    v, c = v_stats.get(i['id']['videoId']), c_stats.get(i['snippet']['channelId'])
                    if v and c:
                        vistas = int(v['statistics'].get('viewCount', 0))
                        subs = int(c['statistics'].get('subscriberCount', 1))
                        
                        if vistas > (subs * 5) and subs <= max_subs:
                            # DISEÑO DE TARJETA VISUAL
                            col_img, col_info = st.columns([1, 2])
                            
                            with col_img:
                                thumb_url = v['snippet']['thumbnails']['high']['url']
                                st.image(thumb_url, use_container_width=True)
                            
                            with col_info:
                                st.subheader(v['snippet']['title'])
                                st.write(f"📺 **Canal:** {v['snippet']['channelTitle']}")
                                # Línea corregida aquí:
                                st.write(f"📈 **Ratio:** {round(vistas/subs, 1)}x  |  👁️ **Vistas:** {vistas:,}")
                                st.link_button("🎥 Ver en YouTube", f"https://youtube.com/watch?v={v['id']}")
                                
                                # Botón de guardado
                                btn_id = f"save_{v['id']}"
                                if st.button(f"📥 Guardar Hallazgo", key=btn_id):
                                    nuevo_oro = pd.DataFrame([{
                                        "Fecha": datetime.now().strftime("%Y-%m-%d"),
                                        "Miniatura": thumb_url,
                                        "Título": v['snippet']['title'],
                                        "Canal": v['snippet']['channelTitle'],
                                        "Vistas": vistas,
                                        "Ratio": f"{round(vistas/subs, 1)}x",
                                        "Link": f"https://youtube.com/watch?v={v['id']}"
                                    }])
                                    st.session_state['database'] = pd.concat([st.session_state['database'], nuevo_oro]).drop_duplicates(subset=['Link'])
                                    st.toast("¡Guardado en la biblioteca!")
                            st.divider()
            except Exception as e:
                st.error(f"Error de sistema: {e}")

with tab2:
    st.header("📂 Tu Galería de Referencias")
    if not st.session_state['database'].empty:
        st.dataframe(
            st.session_state['database'],
            column_config={
                "Miniatura": st.column_config.ImageColumn("Preview"),
                "Link": st.column_config.LinkColumn("Enlace")
            },
            use_container_width=True,
            hide_index=True
        )
        csv = st.session_state['database'].to_csv(index=False).encode('utf-8')
        st.download_button("💾 Descargar CSV de Producción", csv, "biblioteca_velocity.csv", "text/csv")
    else:
        st.info("La biblioteca está vacía.")
