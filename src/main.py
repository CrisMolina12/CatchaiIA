import streamlit as st
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.document_processor import DocumentProcessor
from services.conversation_manager import ConversationManager
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface
from components.document_analysis import render_document_analysis

load_dotenv()

st.set_page_config(
    page_title="CatchAI - Copiloto Conversacional",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 1200px;
    }
    
    /* Main header with improved gradient and typography */
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: #ffffff;
        color: #111827;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 2px solid #e5e7eb;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        font-family: 'Inter', sans-serif;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        color: #111827;
        font-family: 'Inter', sans-serif;
    }
    
    .main-header p {
        margin: 1rem 0 0 0;
        font-size: 1.2rem;
        color: #6b7280;
        font-family: 'Inter', sans-serif;
    }
    
    .gemini-badge {
        display: inline-block;
        background: #f3f4f6;
        color: #111827;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-size: 1rem;
        margin-top: 1rem;
        font-weight: 500;
        border: 1px solid #d1d5db;
        font-family: 'Inter', sans-serif;
    }
    
    /* Welcome section with cleaner design */
    .welcome-section {
        background: #ffffff;
        padding: 3rem 2rem;
        border-radius: 12px;
        text-align: center;
        margin: 2rem 0;
        border: 2px solid #e5e7eb;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .welcome-section h2 {
        color: #111827;
        font-size: 2rem;
        margin-bottom: 1rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
    }
    
    .welcome-section p {
        color: #6b7280;
        font-size: 1.1rem;
        line-height: 1.6;
        max-width: 600px;
        margin: 0 auto 2rem auto;
        font-family: 'Inter', sans-serif;
    }
    
    /* Feature grid with improved cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: #ffffff;
        padding: 2rem 1.5rem;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #9ca3af;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        color: #111827;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    .feature-desc {
        color: #6b7280;
        font-size: 1rem;
        line-height: 1.5;
        font-family: 'Inter', sans-serif;
    }
    
    /* Improved tabs design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f9fafb;
        padding: 8px;
        border-radius: 8px;
        margin-bottom: 2rem;
        border: 1px solid #d1d5db;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 6px;
        color: #6b7280;
        font-weight: 500;
        font-size: 1rem;
        font-family: 'Inter', sans-serif;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #ffffff;
        color: #111827;
    }
    
    .stTabs [aria-selected="true"] {
        background: #111827;
        color: #ffffff;
        font-weight: 600;
    }
    
    /* Typography improvements */
    body {
        font-family: 'Inter', sans-serif;
        color: #111827;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        color: #111827;
    }
    
    .stButton > button {
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    .stButton > button[kind="primary"] {
        background: #111827;
        border: none;
        color: #ffffff;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #374151;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'document_processor' not in st.session_state:
        st.session_state.document_processor = DocumentProcessor()
    
    if 'conversation_manager' not in st.session_state:
        st.session_state.conversation_manager = ConversationManager()
    
    if 'documents_processed' not in st.session_state:
        st.session_state.documents_processed = False
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'processing_results' not in st.session_state:
        st.session_state.processing_results = None
    
    if 'current_files' not in st.session_state:
        st.session_state.current_files = []

def main():
    initialize_session_state()
    
    st.markdown("""
    <div class="main-header">
        <h1>🧠 CatchAI</h1>
        <p>Copiloto Conversacional para Documentos PDF</p>
    </div>
    """, unsafe_allow_html=True)
    
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key or google_api_key == "tu_google_api_key_aqui":
        st.error("⚠️ Por favor, configura tu GOOGLE_API_KEY en el archivo .env")
        st.info("🔗 Obtén tu API key gratuita en: https://aistudio.google.com/app/apikey")
        st.code("""
# En tu archivo .env:
GOOGLE_API_KEY=tu_api_key_real_aqui
        """)
        st.stop()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        render_sidebar()
    
    with col2:
        if st.session_state.documents_processed:
            tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Análisis", "📋 Resumen"])
            
            with tab1:
                render_chat_interface()
            
            with tab2:
                render_document_analysis()
            
            with tab3:
                render_document_summary()
        else:
            st.markdown("""
            <div class="welcome-section">
                <h2>¡Bienvenido a CatchAI!</h2>
                <p>Sube hasta 5 documentos PDF y comienza a hacer preguntas sobre su contenido</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">📄</div>
                    <div class="feature-title">Análisis de PDFs</div>
                    <div class="feature-desc">Procesa hasta 5 documentos PDF simultáneamente</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💬</div>
                    <div class="feature-title">Chat Inteligente</div>
                    <div class="feature-desc">Haz preguntas y obtén respuestas precisas</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <div class="feature-title">Comparaciones</div>
                    <div class="feature-desc">Compara información entre documentos</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📋</div>
                    <div class="feature-title">Resúmenes</div>
                    <div class="feature-desc">Genera resúmenes ejecutivos automáticos</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("👈 Sube algunos documentos PDF en la barra lateral para comenzar")

def render_document_summary():
    st.markdown("""
    <h2 style="color: #ffffff; font-weight: 600; margin-bottom: 1.5rem; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">
        📋 Resumen de Documentos
    </h2>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Generar Resumen Ejecutivo"):
        with st.spinner("Generando resumen con Gemini..."):
            summary = st.session_state.conversation_manager.get_document_summary()
            st.markdown("""
            <h3 style="color: #ffffff; font-weight: 600; margin: 1.5rem 0 1rem 0; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">
                Resumen Ejecutivo
            </h3>
            """, unsafe_allow_html=True)
            st.write(summary)
    
    st.markdown("---")
    
    st.markdown("""
    <h2 style="color: #ffffff; font-weight: 600; margin-bottom: 1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">
        🔍 Comparación de Documentos
    </h2>
    """, unsafe_allow_html=True)
    
    aspect = st.text_input("¿En qué aspecto quieres comparar los documentos?", 
                          placeholder="Ej: metodología, conclusiones, datos...")
    
    if st.button("📊 Comparar") and aspect:
        with st.spinner("Comparando documentos con Gemini..."):
            comparison = st.session_state.conversation_manager.compare_documents(aspect)
            st.markdown("""
            <h3 style="color: #ffffff; font-weight: 600; margin: 1.5rem 0 1rem 0; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">
                Análisis Comparativo
            </h3>
            """, unsafe_allow_html=True)
            st.write(comparison)

if __name__ == "__main__":
    main()
