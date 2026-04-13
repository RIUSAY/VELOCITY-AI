import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Configuración de Identidad
st.set_page_config(page_title="VELOCITY AI - DATABASE", layout="wide")
st.title("🚀 VELOCITY AI: Intel & Performance")

# Inicializar Base de Datos en la sesión si no existe
if 'database' not in st.session_state:
    st.session_state['database'] = pd.DataFrame(columns=["Fecha Registro", "Publicado", "Nicho", "Título", "Vistas", "Ratio", "Link"])

# --- BARRA LATERAL: MANDOS DE FILTRADO ---
with st.sidebar:
    st.header("⚙️ Filtros de Cacería")
    api_key = st.text_input("YouTube API KEY", type="password")
    nicho_input = st.text_input("Nicho Maestro", value="mystery")
    
    st.divider()
    
    # NUEVO: Filtro de Tiempo de Publicación
    tiempo = st.selectbox("Buscar videos de:", ["Últimas 24h", "Última semana", "Último mes", "Siempre"], index=1)
    
    idioma = st.selectbox("Mercado", ["en", "es"])
    max_subs = st.number_input("Máximo Suscriptores", value=200000)
    min_vistas = st.number_input("Mínimo de Vistas", value=5000)

    if st.button("🗑️ Limpiar Base de Datos"):
        st.session_state['database'] = pd.DataFrame(columns=["Fecha Registro", "Publicado", "Nicho", "Título", "Vistas", "Ratio", "Link"])
        st.rerun()

# --- LÓGICA DE TIEMPO ---
def obtener_fecha_filtro(opcion):
    ahora = datetime.utcnow()
    if opcion == "Últimas 24h": return (ahora - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    if opcion == "Última semana": return (ahora - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
    if opcion == "Último mes": return (ahora - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
    return None

# --- PANEL PRINCIPAL ---
tab1, tab2 = st.tabs(["🔍 Radar en Vivo", "📂 Base de Datos de Oros"])

with tab1:
    if st.button("🔥 EJECUTAR ESCANEO"):
        if not api_key:
            st.error("Falta API KEY")
        else:
            try:
                youtube = build('youtube', 'v3', developerKey=api_key)
                fecha_limite = obtener_fecha_filtro(tiempo)
                
                res = youtube.search().list(
                    q=nicho_input, part='snippet', maxResults=50, type='video',
                    order='viewCount', publishedAfter=fecha_limite,
                    regionCode='US' if idioma=='en' else 'MX'
                ).execute()
                
                v_ids = [i['id']['videoId'] for i in res['items']]
                v_data = youtube.videos().list(part='statistics,snippet', id=','.join(v_ids)).execute()['items']
                v_stats = {v['id']: v for v in v_data}
                
                c_ids = list(set([i['snippet']['channelId'] for i in res['items']]))
                c_stats = {c['id']: c for c in youtube.channels().list(part='statistics', id=','.join(c_ids)).execute()['items']}

                anomalias = []
                for i in res['items']:
                    v, c = v_stats.get(i['id']['videoId']), c_stats.get(i['snippet']['channelId'])
                    if v and c:
                        vistas = int(v['statistics'].get('viewCount', 0))
                        subs = int(c['statistics'].get('subscriberCount', 1))
                        # Fecha de publicación simplificada
                        pub_date = v['snippet']['publishedAt'][:10] 
                        
                        if vistas >= min_vistas and subs <= max_subs and vistas > (subs * 5):
                            anomalias.append({
                                "Fecha Registro": datetime.now().strftime("%Y-%m-%d"),
                                "Publicado": pub_date,
                                "Nicho": nicho_input,
                                "Título": i['snippet']['title'],
                                "Vistas": vistas,
                                "Ratio": f"{round(vistas/subs, 1)}x",
                                "Link": f"https://youtube.com/watch?v={v['id']}"
                            })

                if anomalias:
                    df_temp = pd.DataFrame(anomalias)
                    st.write("### 💎 Hallazgos con Métricas")
                    # Formatear vistas con comas para que sea legible
                    df_temp['Vistas'] = df_temp['Vistas'].apply(lambda x: "{:,}".format(x))
                    st.dataframe(df_temp, use_container_width=True)
                    
                    if st.button("📥 GUARDAR HALLAZGOS"):
                        st.session_state['database'] = pd.concat([st.session_state['database'], df_temp]).drop_duplicates(subset=['Link'])
                        st.success("¡Sincronizado!")
                else:
                    st.warning("No se encontraron videos que superen nuestro estándar.")
            except Exception as e:
                st.error(f"Error de sistema: {e}")

with tab2:
    st.header("📂 Historial de Rendimiento")
    if not st.session_state['database'].empty:
        st.dataframe(st.session_state['database'], use_container_width=True)
        csv = st.session_state['database'].to_csv(index=False).encode('utf-8')
        st.download_button("💾 Descargar Reporte CSV", csv, "base_datos_velocity.csv", "text/csv")
    else:
        st.info("Escanea y guarda videos para ver el historial.")
