import streamlit as st
from services.conversation_manager import ConversationManager

def render_sidebar():
    """Renderiza la barra lateral con carga de documentos"""
    
    st.sidebar.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Simplified file uploader with high contrast */
    .stFileUploader > div > div > div > div {
        text-align: center;
        padding: 2rem;
        border: 2px dashed #6b7280;
        border-radius: 8px;
        background: #ffffff;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .stFileUploader > div > div > div > div:hover {
        border-color: #111827;
        background: #f9fafb;
    }
    
    .stFileUploader > div > div > div > div::before {
        content: "📁 Arrastra tus PDFs aquí o haz clic para seleccionar";
        display: block;
        font-size: 16px;
        color: #111827;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .stFileUploader > div > div > div > div::after {
        content: "Máximo 5 archivos PDF • Límite 200MB por archivo";
        display: block;
        font-size: 12px;
        color: #6b7280;
        margin-top: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .stFileUploader label {
        font-weight: 600 !important;
        color: #111827 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
    }
    
    /* Simplified sidebar sections with white backgrounds */
    .sidebar-section {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        text-align: center;
        border: 2px solid #e5e7eb;
    }
    
    .sidebar-section h3 {
        margin: 0;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: #111827;
    }
    
    .status-section {
        background: #f9fafb;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        margin-bottom: 1rem;
    }
    
    .status-section h4 {
        margin: 0 0 1rem 0;
        color: #111827;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("""
    <div class="sidebar-section">
        <h3>📁 Gestión de Documentos</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("**📤 Subir Archivos PDF**")
    
    uploaded_files = st.sidebar.file_uploader(
        "Selecciona hasta 5 PDFs",
        type=['pdf'],
        accept_multiple_files=True,
        help="Máximo 5 archivos PDF • Límite 200MB por archivo",
        label_visibility="collapsed"
    )
    
    if not uploaded_files:
        st.sidebar.info("💡 Sube hasta 5 documentos PDF para análisis")
    
    if uploaded_files:
        current_file_names = [f.name for f in uploaded_files]
        if 'current_files' not in st.session_state:
            st.session_state.current_files = []
        
        # Si los archivos cambiaron, limpiar estado
        if st.session_state.current_files != current_file_names:
            if st.session_state.current_files:  # Solo si había archivos anteriores
                st.sidebar.info("🔄 Archivos cambiados - Estado limpiado")
                reset_system()
            st.session_state.current_files = current_file_names
    
    if uploaded_files:
        if len(uploaded_files) > 5:
            st.sidebar.error("⚠️ Máximo 5 archivos permitidos")
            return
        
        # Mostrar archivos seleccionados
        st.sidebar.write("**Archivos seleccionados:**")
        total_size = 0
        for file in uploaded_files:
            size_mb = len(file.getvalue()) / (1024 * 1024)
            total_size += size_mb
            st.sidebar.write(f"• {file.name} ({size_mb:.1f} MB)")
        
        st.sidebar.write(f"**Tamaño total:** {total_size:.1f} MB")
        
        # Botón de procesamiento
        if st.sidebar.button("🚀 Procesar Documentos", type="primary"):
            process_documents(uploaded_files)
    
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("""
    <div class="status-section">
        <h4>📊 Estado del Sistema</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.documents_processed:
        st.sidebar.success("✅ Documentos procesados")
        if st.session_state.processing_results:
            results = st.session_state.processing_results
            st.sidebar.write(f"📄 {results['total_documents']} chunks creados")
            st.sidebar.write(f"📁 {len(results['file_summaries'])} archivos")
    else:
        st.sidebar.info("⏳ Esperando documentos...")
    
    if st.sidebar.button("🔄 Reiniciar Sistema", help="Limpia todos los datos"):
        reset_system()

def process_documents(uploaded_files):
    """Procesa los documentos subidos"""
    try:
        with st.spinner("Procesando documentos..."):
            # Procesar documentos
            results = st.session_state.document_processor.process_pdfs(uploaded_files)
            
            # Actualizar conversation manager
            st.session_state.conversation_manager = ConversationManager(
                vector_store=results['vector_store']
            )
            
            # Actualizar estado
            st.session_state.documents_processed = True
            st.session_state.processing_results = results
            st.session_state.chat_history = []
            
            st.success(f"✅ {len(uploaded_files)} documentos procesados correctamente!")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error al procesar documentos: {str(e)}")

def reset_system():
    """Reinicia el sistema"""
    st.session_state.documents_processed = False
    st.session_state.chat_history = []
    st.session_state.processing_results = None
    st.session_state.current_files = []
    st.session_state.conversation_manager = ConversationManager()
    st.rerun()
