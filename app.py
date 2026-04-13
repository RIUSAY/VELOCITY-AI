%%writefile app.py
import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

st.set_page_config(page_title="VELOCITY AI - DATABASE", layout="wide")
st.title("🚀 VELOCITY AI: Intel & Database")

# Inicializar Base de Datos en la sesión si no existe
if 'database' not in st.session_state:
    st.session_state['database'] = pd.DataFrame(columns=["Fecha", "Nicho", "Título", "Ratio", "Vistas", "Link"])

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("YouTube API KEY", type="password")
    nicho_input = st.text_input("Nicho Maestro", value="ancient mysteries")
    idioma = st.selectbox("Mercado", ["en", "es"])
    max_subs = st.number_input("Límite Suscriptores", value=150000)
    
    st.divider()
    if st.button("🗑️ Limpiar Base de Datos"):
        st.session_state['database'] = pd.DataFrame(columns=["Fecha", "Nicho", "Título", "Ratio", "Vistas", "Link"])
        st.rerun()

# --- PANEL PRINCIPAL: PESTAÑAS ---
tab1, tab2 = st.tabs(["🔍 Radar de Cacería", "📂 Base de Datos de Éxitos"])

with tab1:
    if st.button("🔥 EJECUTAR ESCANEO"):
        if not api_key:
            st.error("Falta API KEY")
        else:
            youtube = build('youtube', 'v3', developerKey=api_key)
            res = youtube.search().list(q=nicho_input, part='snippet', maxResults=50, 
                                        type='video', regionCode='US' if idioma=='en' else 'MX').execute()
            
            v_ids = [i['id']['videoId'] for i in res['items']]
            v_data = youtube.videos().list(part='statistics', id=','.join(v_ids)).execute()['items']
            v_stats = {v['id']: v for v in v_data}
            c_ids = list(set([i['snippet']['channelId'] for i in res['items']]))
            c_stats = {c['id']: c for c in youtube.channels().list(part='statistics', id=','.join(c_ids)).execute()['items']}

            anomalias = []
            for i in res['items']:
                v, c = v_stats.get(i['id']['videoId']), c_stats.get(i['snippet']['channelId'])
                if v and c:
                    vistas, subs = int(v['statistics'].get('viewCount', 0)), int(c['statistics'].get('subscriberCount', 1))
                    if vistas > (subs * 5) and subs <= max_subs:
                        anomalias.append({
                            "Fecha": datetime.now().strftime("%Y-%m-%d"),
                            "Nicho": nicho_input,
                            "Título": i['snippet']['title'],
                            "Ratio": round(vistas/subs, 1),
                            "Vistas": vistas,
                            "Link": f"https://youtube.com/watch?v={v['id']}"
                        })

            if anomalias:
                df_temp = pd.DataFrame(anomalias)
                st.write("### 💎 Hallazgos del Momento")
                st.dataframe(df_temp)
                
                if st.button("📥 GUARDAR TODO EN BASE DE DATOS"):
                    st.session_state['database'] = pd.concat([st.session_state['database'], df_temp]).drop_duplicates(subset=['Link'])
                    st.success("¡Datos sincronizados con la Base de Datos Central!")
            else:
                st.warning("No se encontraron anomalías.")

with tab2:
    st.header("📂 Historial Maestro de Palabras y Videos")
    if not st.session_state['database'].empty:
        st.dataframe(st.session_state['database'], use_container_width=True)
        
        # Botón para descargar a Excel/CSV para el equipo
        csv = st.session_state['database'].to_csv(index=False).encode('utf-8')
        st.download_button("💾 Descargar Reporte para Producción", csv, "base_datos_velocity.csv", "text/csv")
        
        st.write("### 📈 Análisis de Palabras Clave")
        palabras_top = st.session_state['database']['Nicho'].value_counts()
        st.bar_chart(palabras_top)
    else:
        st.info("La base de datos está vacía. Empieza a escanear en la pestaña 1.")
