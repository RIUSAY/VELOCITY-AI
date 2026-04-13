import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from deep_translator import GoogleTranslator

# Configuración de página
st.set_page_config(page_title="VIRALYT CLONE - FACTORY", layout="wide")
st.title("🚀 VELOCITY AI: Market Intelligence")

# Barra lateral para configuración
with st.sidebar:
    st.header("Configuración de Mando")
    api_key = st.text_input("YouTube API KEY", type="password")
    nicho = st.text_input("Nicho a escanear", value="mystery documentary")
    limite_subs = st.slider("Máximo de Suscriptores", 1000, 500000, 200000)

if st.button("🔍 INICIAR ESCANEO MASIVO"):
    if not api_key:
        st.error("Introduce tu API KEY para facturar.")
    else:
        youtube = build('youtube', 'v3', developerKey=api_key)
        st.info(f"Escaneando nicho: {nicho}...")
        
        # Lógica del Radar
        res = youtube.search().list(q=nicho, part='snippet', maxResults=50, 
                                    order='viewCount', type='video', regionCode='US').execute()
        
        v_ids = [i['id']['videoId'] for i in res['items']]
        v_data = youtube.videos().list(part='statistics,contentDetails', id=','.join(v_ids)).execute()['items']
        v_stats = {v['id']: v for v in v_data}
        
        c_ids = list(set([i['snippet']['channelId'] for i in res['items']]))
        c_data = youtube.channels().list(part='statistics', id=','.join(c_ids)).execute()['items']
        c_stats = {c['id']: c for c in c_data}

        anomalias = []
        for i in res['items']:
            v, c = v_stats.get(i['id']['videoId']), c_stats.get(i['snippet']['channelId'])
            if v and c:
                vistas, subs = int(v['statistics'].get('viewCount', 0)), int(c['statistics'].get('subscriberCount', 1))
                if vistas > (subs * 5) and subs < limite_subs:
                    anomalias.append({
                        "Ratio": round(vistas/subs, 1),
                        "Vistas": vistas,
                        "Subs": subs,
                        "Canal": i['snippet']['channelTitle'],
                        "Título": i['snippet']['title'],
                        "Link": f"https://youtube.com/watch?v={v['id']}"
                    })

        if anomalias:
            df = pd.DataFrame(anomalias)
            st.success(f"¡Se encontraron {len(df)} minas de oro!")
            st.dataframe(df.sort_values(by="Ratio", ascending=False), use_container_width=True)
        else:
            st.warning("No se detectaron anomalías con estos filtros.")
