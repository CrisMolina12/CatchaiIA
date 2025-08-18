from typing import List, Dict, Any, Optional
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import os
import time
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import hashlib

class ConversationManager:
    def __init__(self, vector_store=None):
        self.llm = None
        self.vector_store = vector_store
        self.conversation_chain = None
        
        self._initialize_gemini()
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        if vector_store:
            self._setup_conversation_chain()
    
    def _get_api_key_hash(self, api_key: str) -> str:
        """Generate a hash of the API key for tracking"""
        if not api_key:
            return ""
        return hashlib.md5(api_key.encode()).hexdigest()[:16]
    
    def _initialize_gemini(self):
        """Initialize only Google Gemini with enhanced account change detection"""
        google_api_key = os.getenv("GOOGLE_API_KEY")
        current_hash = self._get_api_key_hash(google_api_key)
        
        if hasattr(st.session_state, 'conversation_api_hash'):
            if st.session_state.conversation_api_hash != current_hash:
                print(f"[v0] 🔄 API key change detected in ConversationManager")
                self._clear_conversation_data()
        
        st.session_state.conversation_api_hash = current_hash
        
        if not google_api_key or google_api_key == "tu_google_api_key_aqui":
            st.error("⚠️ GOOGLE_API_KEY no configurada. Por favor configura tu API key de Google.")
            st.info("🔗 Obtén tu API key gratuita en: https://makersuite.google.com/app/apikey")
            st.stop()
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.1,
                google_api_key=google_api_key,
                max_output_tokens=2048
            )
            print(f"[v0] ✅ Gemini inicializado exitosamente con cuenta: {current_hash}")
        except Exception as e:
            st.error(f"❌ Error inicializando Gemini: {e}")
            st.info("Verifica que tu GOOGLE_API_KEY sea válida")
            st.stop()
    
    def _clear_conversation_data(self):
        """Clear conversation-specific data when account changes"""
        if hasattr(self, 'memory'):
            self.memory.clear()
        
        # Clear conversation chain to force recreation
        self.conversation_chain = None
        
        # Clear related session state
        conversation_keys = [
            'chat_history',
            'conversation_manager',
            'processing_results'
        ]
        
        for key in conversation_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        print("[v0] 🔄 Conversation data cleared for account change")

    def _get_diverse_context(self, question: str, k_per_doc: int = 5) -> List[Document]:
        """Get diverse chunks from all documents to ensure all PDFs are represented"""
        if not self.vector_store:
            return []
        
        try:
            # Get all unique document sources
            all_docs = self.vector_store.get()
            unique_sources = set()
            if all_docs and 'metadatas' in all_docs:
                for metadata in all_docs['metadatas']:
                    if metadata and 'source' in metadata:
                        unique_sources.add(metadata['source'])
            
            print(f"[v0] Found {len(unique_sources)} unique documents: {list(unique_sources)}")
            
            diverse_docs = []
            
            # Get chunks from each document
            for source in unique_sources:
                try:
                    # Search with filter for specific document
                    source_docs = self.vector_store.similarity_search(
                        question,
                        k=k_per_doc,
                        filter={"source": source}
                    )
                    diverse_docs.extend(source_docs)
                    print(f"[v0] Retrieved {len(source_docs)} chunks from {source}")
                except Exception as e:
                    print(f"[v0] Error retrieving from {source}: {e}")
                    # Fallback: get all docs and filter manually
                    all_source_docs = self.vector_store.similarity_search(question, k=25)
                    filtered_docs = [doc for doc in all_source_docs if doc.metadata.get('source') == source]
                    diverse_docs.extend(filtered_docs[:k_per_doc])
            
            print(f"[v0] Total diverse chunks retrieved: {len(diverse_docs)}")
            return diverse_docs
            
        except Exception as e:
            print(f"[v0] Error in diverse retrieval: {e}")
            # Fallback to regular retrieval with higher k
            return self.vector_store.similarity_search(question, k=25)

    def _setup_conversation_chain(self):
        """Configura la cadena conversacional"""
        custom_prompt = PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template="""Eres un asistente especializado en analizar documentos PDF. Responde de forma concisa y directa.

Contexto de múltiples documentos: {context}

Pregunta: {question}

Instrucciones IMPORTANTES:
- DEBES analizar TODOS los documentos diferentes proporcionados en el contexto
- Si hay documentos de CV, horarios, análisis de riesgos, etc., menciona información de CADA UNO
- Identifica claramente qué información viene de qué archivo
- NO te enfoques solo en un tipo de documento
- Si la pregunta es general, proporciona información de TODOS los archivos disponibles

Respuesta:"""
        )
        
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 25}
        )
        
        self.conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": custom_prompt}
        )
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Procesa una pregunta y devuelve la respuesta"""
        if not self.conversation_chain:
            return {
                "answer": "Por favor, sube algunos documentos PDF primero.",
                "source_documents": []
            }
        
        try:
            print(f"[v0] Procesando pregunta: {question}")
            print(f"[v0] Usando Gemini con cuenta: {st.session_state.get('conversation_api_hash', 'unknown')}")
            
            diverse_docs = self._get_diverse_context(question)
            
            context_by_source = {}
            for doc in diverse_docs:
                source = doc.metadata.get('source', 'unknown')
                if source not in context_by_source:
                    context_by_source[source] = []
                context_by_source[source].append(doc.page_content)
            
            structured_context = ""
            for source, contents in context_by_source.items():
                structured_context += f"\n--- Documento: {source} ---\n"
                structured_context += "\n".join(contents[:3])
                structured_context += "\n"
            
            print(f"[v0] Context built from {len(context_by_source)} documents")
            
            prompt_text = f"""Eres un asistente especializado en analizar documentos PDF. Responde de forma concisa y directa.

Contexto de múltiples documentos: {structured_context}

Pregunta: {question}

Instrucciones IMPORTANTES:
- DEBES analizar TODOS los documentos diferentes proporcionados en el contexto
- Si hay documentos de CV, horarios, análisis de riesgos, etc., menciona información de CADA UNO
- Identifica claramente qué información viene de qué archivo
- NO te enfoques solo en un tipo de documento
- Si la pregunta es general, proporciona información de TODOS los archivos disponibles

Respuesta:"""
            
            start_time = time.time()
            response = self.llm.invoke(prompt_text)
            end_time = time.time()
            
            print(f"[v0] Respuesta generada en {end_time - start_time:.2f} segundos")
            
            source_files = set(context_by_source.keys())
            print(f"[v0] Archivos consultados: {list(source_files)}")
            
            return {
                "answer": response.content,
                "source_documents": diverse_docs,
                "chat_history": self.memory.chat_memory.messages
            }
        
        except Exception as e:
            print(f"[v0] Error: {type(e).__name__}: {str(e)}")
            error_message = str(e).lower()
            
            if any(keyword in error_message for keyword in ["429", "quota", "rate limit", "exceeded", "too many requests"]):
                return {
                    "answer": """⚠️ **Límite de Gemini alcanzado**
                    
**Posibles soluciones:**
1. **Cambiar de cuenta Google:** Usa el botón "Reiniciar Sesión Completa" en la barra lateral
2. Espera 1-2 minutos y vuelve a intentar
3. Verifica tu cuota en https://aistudio.google.com/
4. Considera usar menos texto en tus preguntas

💡 **Tip:** Si tienes otra cuenta Google, cámbiala para obtener créditos frescos""",
                    "source_documents": [],
                    "rate_limited": True
                }
            elif any(keyword in error_message for keyword in ["api key", "authentication", "unauthorized", "401"]):
                return {
                    "answer": "❌ Error de autenticación: Verifica que tu GOOGLE_API_KEY esté configurada correctamente",
                    "source_documents": [],
                    "error_type": "auth_error"
                }
            else:
                return {
                    "answer": f"❌ Error: {str(e)}",
                    "source_documents": [],
                    "error_type": "unknown_error"
                }

    def get_document_summary(self) -> str:
        """Genera un resumen de todos los documentos"""
        if not self.vector_store:
            return "No hay documentos cargados."
        
        summary_prompt = """
        Basándote en los documentos cargados, proporciona un resumen ejecutivo que incluya:
        1. Temas principales tratados
        2. Puntos clave de cada documento
        3. Conexiones entre documentos (si las hay)
        
        Mantén el resumen conciso pero informativo.
        """
        
        try:
            result = self.ask_question(summary_prompt)
            return result["answer"]
        except:
            return "No se pudo generar el resumen."
    
    def compare_documents(self, aspect: str) -> str:
        """Compara documentos en un aspecto específico"""
        comparison_prompt = f"""
        Compara los documentos cargados en términos de: {aspect}
        
        Proporciona:
        1. Similitudes encontradas
        2. Diferencias principales
        3. Análisis comparativo
        
        Estructura tu respuesta de manera clara y organizada.
        """
        
        try:
            result = self.ask_question(comparison_prompt)
            return result["answer"]
        except:
            return "No se pudo realizar la comparación."
