with tab3:
    st.header("🛡️ Auditoría de Canal: Análisis Visual")
    c_input = st.text_input("Pega el ID o @usuario (Ej: @ZkeletonIA)", key="c_audit_v7")
    
    if st.button("Auditar Canal"):
        if not api_key:
            st.error("⚠️ Configura la API KEY primero.")
        else:
            try:
                youtube = build('youtube', 'v3', developerKey=api_key)
                handle = c_input.split("/")[-1].replace("@", "")
                
                # Búsqueda de información del canal
                if c_input.startswith("UC"):
                    c_res = youtube.channels().list(part='snippet,statistics', id=c_input).execute()
                else:
                    c_res = youtube.channels().list(part='snippet,statistics', forHandle=handle).execute()
                
                if c_res.get('items'):
                    det = c_res['items'][0]
                    c_id = det['id']
                    stats = det['statistics']
                    
                    # --- INFORMACIÓN GENERAL ---
                    col_logo, col_info = st.columns([1, 4])
                    with col_logo:
                        st.image(det['snippet']['thumbnails']['high']['url'], use_container_width=True)
                    with col_info:
                        st.title(det['snippet']['title'])
                        st.write(f"📅 **Se unió:** {det['snippet']['publishedAt'][:10]}")
                        st.write(f"📝 **Descripción:** {det['snippet']['description'][:350]}...")
                    
                    st.divider()
                    
                    # --- MÉTRICAS DE VOLUMEN ---
                    m1, m2, m3 = st.columns(3)
                    vistas_totales = int(stats.get('viewCount', 0))
                    m1.metric("Suscriptores", f"{int(stats.get('subscriberCount', 0)):,}")
                    m2.metric("Videos Subidos", stats.get('videoCount', 0))
                    m3.metric("Visualizaciones Totales", f"{vistas_totales:,}")

                    # --- GALERÍA DE VIDEOS VIRALES (DISEÑO PEQUEÑO) ---
                    st.divider()
                    st.subheader("🔥 Top Videos Virales (Referencia Visual)")
                    
                    # Nota: Esta función consume 100 unidades de cuota.
                    v_list = youtube.search().list(
                        channelId=c_id, 
                        part='snippet', 
                        order='viewCount', 
                        maxResults=6, 
                        type='video'
                    ).execute()
                    
                    # Mostrar en una cuadrícula de 3 columnas para que sean pequeñas
                    cols = st.columns(3)
                    for idx, vid in enumerate(v_list.get('items', [])):
                        with cols[idx % 3]:
                            st.image(vid['snippet']['thumbnails']['high']['url'], use_container_width=True)
                            st.caption(f"**{vid['snippet']['title'][:50]}...**")
                            st.write(f"🔗 [Link pequeño](https://youtube.com/watch?v={vid['id']['videoId']})")
                            st.write("---")
                else:
                    st.error("❌ Canal no encontrado. Revisa el ID o el @usuario.")
                    
            except Exception as e:
                if "quota" in str(e).lower():
                    st.error("🚫 Error: Has agotado tu cuota diaria de YouTube API. Debes esperar a que se reinicie (medianoche PT) o usar otra API KEY.")
                else:
                    st.error(f"⚠️ Error en Auditoría: {e}")
