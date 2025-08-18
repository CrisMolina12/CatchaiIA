import streamlit as st

def render_chat_interface():
    """Renderiza la interfaz de chat"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
        font-family: 'Inter', sans-serif;
    }
    
    .user-message {
        background: #f1f5f9;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 4px 18px;
        margin: 1rem 0 1rem auto;
        max-width: 80%;
        border-left: 4px solid #3b82f6;
    }
    
    .assistant-message {
        background: #ffffff;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 18px 4px;
        margin: 1rem auto 1rem 0;
        max-width: 85%;
        border-left: 4px solid #10b981;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .message-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .user-header { color: #3b82f6; }
    .assistant-header { color: #10b981; }
    
    .message-content {
        color: #374151;
        line-height: 1.6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Eliminar estilos que causan bloques blancos */
    .stMarkdown { margin: 0 !important; }
    .element-container { margin: 0 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chat-header">
        <h2 style="margin:0; font-size:1.8rem;">💬 Chat con tus Documentos</h2>
        <p style="margin:0.5rem 0 0 0; opacity:0.9;">Haz preguntas inteligentes sobre el contenido de tus PDFs</p>
    </div>
    """, unsafe_allow_html=True)
    
    for message in st.session_state.chat_history:
        render_message(message)
    
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_question = st.text_input(
                "Pregunta:",
                placeholder="Ej: ¿Cuáles son los puntos principales del documento?",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.form_submit_button("Enviar", type="primary")
    
    if submit_button and user_question:
        process_question(user_question)
    
    render_suggested_questions()

def render_message(message):
    """Renderiza un mensaje del chat"""
    if message["role"] == "user":
        st.markdown(f"""
        <div class="user-message">
            <div class="message-header user-header">👤 Tú</div>
            <div class="message-content"><strong>{message['content']}</strong></div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <div class="message-header assistant-header">🤖 CatchAI</div>
            <div class="message-content">{message['content']}</div>
        </div>
        """, unsafe_allow_html=True)

        if "sources" in message and message["sources"]:
            with st.expander("📚 Ver fuentes", expanded=False):
                for i, source in enumerate(message["sources"]):
                    st.write(f"**📄 Fuente {i+1}:** {source.metadata.get('source_file', 'Desconocido')}")
                    st.write(f"**📖 Página:** {source.metadata.get('page', 'N/A')}")
                    st.write(f"_{source.page_content[:200]}..._")
                    st.write("---")

def process_question(question):
    """Procesa una pregunta del usuario"""
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })
    
    with st.spinner("Pensando..."):
        result = st.session_state.conversation_manager.ask_question(question)
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("source_documents", [])
        })
    
    st.rerun()

def render_suggested_questions():
    """Renderiza preguntas sugeridas"""
    st.markdown("---")
    st.markdown("""
    <h3 style="color: #ffffff; font-weight: 600; margin-bottom: 1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">
        💡 Preguntas Sugeridas
    </h3>
    """, unsafe_allow_html=True)
    
    suggestions = [
        "¿Cuáles son los puntos principales de los documentos?",
        "¿Hay información contradictoria entre los documentos?",
        "¿Qué metodología se utiliza en estos documentos?",
        "¿Cuáles son las conclusiones más importantes?",
        "¿Qué datos numéricos relevantes encuentras?"
    ]
    
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(
                suggestion, 
                key=f"suggestion_{i}",
                help="Click para hacer esta pregunta"
            ):
                process_question(suggestion)
