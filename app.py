with tab3:
    st.header("🛡️ Auditoría de Canal")
    canal_input = st.text_input("Pega el ID del Canal o URL del Canal", key="c_input")
    
    if st.button("Auditar Canal"):
        if not api_key:
            st.error("⚠️ Configura la API KEY primero.")
        elif not canal_input:
            st.warning("⚠️ Por favor, ingresa un ID o URL de canal.")
        else:
            try:
                # LÓGICA DE LIMPIEZA DEL CEO: Extraer ID si pegas una URL
                # Maneja: youtube.com/channel/UCxxxx o youtube.com/@usuario
                c_id = canal_input.split("/")[-1] if "/" in canal_input else canal_input
                
                youtube = build('youtube', 'v3', developerKey=api_key)
                
                # Paso 1: Buscar información básica del canal
                c_res = youtube.channels().list(
                    part='snippet,statistics,brandingSettings', 
                    id=c_id if c_id.startswith('UC') else None,
                    forHandle=c_id if not c_id.startswith('UC') else None
                ).execute()
                
                if 'items' in c_res and len(c_res['items']) > 0:
                    c_det = c_res['items'][0]
                    col_a, col_b = st.columns([1, 3])
                    
                    with col_a:
                        st.image(c_det['snippet']['thumbnails']['high']['url'], use_container_width=True)
                    
                    with col_b:
                        st.title(c_det['snippet']['title'])
                        st.write(f"✅ **Descripción:** {c_det['snippet']['description'][:300]}...")
                        
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Suscriptores", f"{int(c_det['statistics'].get('subscriberCount', 0)):,}")
                        m2.metric("Videos", f"{int(c_det['statistics'].get('videoCount', 0)):,}")
                        m3.metric("Vistas Totales", f"{int(c_det['statistics'].get('viewCount', 0)):,}")

                    st.write("---")
                    st.subheader("🔝 Top 5 Videos con más Vistas")
                    
                    # Paso 2: Buscar los videos más potentes del canal
                    v_list = youtube.search().list(
                        channelId=c_det['id'],
                        part='snippet',
                        order='viewCount',
                        maxResults=5,
                        type='video'
                    ).execute()
                    
                    if 'items' in v_list:
                        for vid in v_list['items']:
                            v_id = vid['id']['videoId']
                            st.write(f"▶️ **{vid['snippet']['title']}**")
                            st.write(f"🔗 ID: `{v_id}` | [Abrir en YouTube](https://youtube.com/watch?v={v_id})")
                            st.divider()
                    else:
                        st.info("No se pudieron cargar los videos populares de este canal.")
                else:
                    st.error("❌ No se encontró ningún canal. Asegúrate de usar el ID que empieza con 'UC' o el @usuario correctamente.")
                    
            except Exception as e:
                st.error(f"⚠️ Error de Auditoría: {str(e)}")
