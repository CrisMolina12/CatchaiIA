import streamlit as st
import pandas as pd

def render_document_analysis():
    """Renderiza el análisis de documentos con mejor contraste visual"""
    
    st.markdown("""
    <style>
    .analysis-title {
        color: #ffffff !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important;
        margin-bottom: 1rem !important;
    }
    .section-title {
        color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        border-left: 4px solid #3b82f6 !important;
        padding-left: 1rem !important;
        margin: 1.5rem 0 1rem 0 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    .file-name {
        background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
        color: white !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        margin: 1rem 0 0.5rem 0 !important;
        display: inline-block !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
    }
    .file-details {
        color: #e2e8f0 !important;
        font-size: 0.9rem !important;
        margin-left: 1rem !important;
        line-height: 1.6 !important;
    }
    .theme-card {
        background: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
    }
    .theme-title {
        color: #60a5fa !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem !important;
    }
    .theme-description {
        color: #cbd5e1 !important;
        line-height: 1.5 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="analysis-title">📊 Análisis de Documentos</div>', unsafe_allow_html=True)
    
    if not st.session_state.processing_results:
        st.info("No hay documentos procesados para analizar.")
        return
    
    results = st.session_state.processing_results
    
    try:
        # Métricas generales con validación
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_docs = results.get('total_documents', 0)
            st.metric("📄 Total Chunks", int(total_docs) if total_docs else 0)
        
        with col2:
            file_count = len(results.get('file_summaries', {}))
            st.metric("📁 Archivos", file_count)
        
        with col3:
            total_pages = 0
            file_summaries = results.get('file_summaries', {})
            for info in file_summaries.values():
                if isinstance(info, dict) and 'pages' in info:
                    pages = info['pages']
                    if isinstance(pages, (int, float)):
                        total_pages += int(pages)
            st.metric("📖 Total Páginas", total_pages)
        
        st.markdown('<div class="section-title">📋 Detalle de Archivos</div>', unsafe_allow_html=True)
        
        file_summaries = results.get('file_summaries', {})
        if file_summaries:
            for filename, info in file_summaries.items():
                if isinstance(info, dict):
                    pages = info.get('pages', 0)
                    chunks = info.get('chunks', 0)
                    size = info.get('size', 0)
                    
                    # Convert to safe types and display with better styling
                    pages = int(pages) if isinstance(pages, (int, float)) else 0
                    chunks = int(chunks) if isinstance(chunks, (int, float)) else 0
                    size_mb = round(size / (1024 * 1024), 2) if isinstance(size, (int, float)) and size > 0 else 0
                    
                    st.markdown(f'<div class="file-name">📄 {filename}</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="file-details">
                        • <strong>Páginas:</strong> {pages}<br>
                        • <strong>Chunks:</strong> {chunks}<br>
                        • <strong>Tamaño:</strong> {size_mb} MB
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("No hay datos de archivos para mostrar.")
        
        st.markdown('<div class="section-title">🏷️ Análisis Temático</div>', unsafe_allow_html=True)
        
        if st.button("🔍 Identificar Temas Principales"):
            with st.spinner("Analizando temas..."):
                themes = identify_themes()
                
                if themes:
                    for theme in themes:
                        if isinstance(theme, dict):
                            topic = theme.get('topic', 'Tema sin nombre')
                            description = theme.get('description', 'Sin descripción')
                            
                            st.markdown(f'''
                            <div class="theme-card">
                                <div class="theme-title">{topic}</div>
                                <div class="theme-description">{description}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                else:
                    st.info("No se pudieron identificar temas específicos.")
    
    except Exception as e:
        st.error("Error al mostrar el análisis de documentos. Intenta procesar los documentos nuevamente.")

def identify_themes():
    """Identifica temas principales en los documentos"""
    theme_prompt = """
    Analiza todos los documentos cargados e identifica los 3-5 temas principales.
    
    Para cada tema, proporciona:
    1. Nombre del tema
    2. Descripción breve
    3. Documentos donde aparece
    
    Formato de respuesta:
    TEMA: [Nombre del tema]
    DESCRIPCIÓN: [Descripción breve]
    DOCUMENTOS: [Lista de documentos]
    ---
    """
    
    try:
        if not hasattr(st.session_state, 'conversation_manager') or not st.session_state.conversation_manager:
            return []
            
        result = st.session_state.conversation_manager.ask_question(theme_prompt)
        
        if not result or 'answer' not in result:
            return []
        
        # Parsear respuesta (simplificado)
        themes = []
        sections = result["answer"].split("---")
        
        for section in sections:
            if "TEMA:" in section:
                lines = section.strip().split("\n")
                theme = {}
                for line in lines:
                    if line.startswith("TEMA:"):
                        theme['topic'] = line.replace("TEMA:", "").strip()
                    elif line.startswith("DESCRIPCIÓN:"):
                        theme['description'] = line.replace("DESCRIPCIÓN:", "").strip()
                
                if theme and theme.get('topic'):
                    themes.append(theme)
        
        return themes
    
    except Exception as e:
        return []
