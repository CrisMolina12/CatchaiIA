import os
import tempfile
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import streamlit as st
import hashlib
import shutil

class DocumentProcessor:
    def __init__(self):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not google_api_key:
            st.error("GOOGLE_API_KEY no configurada")
            st.stop()
        
        current_hash = self._get_api_key_hash(google_api_key)
        if hasattr(st.session_state, 'processor_api_hash'):
            if st.session_state.processor_api_hash != current_hash:
                print(f"[DEBUG] API key change detected in DocumentProcessor")
                self._cleanup_old_data()
        
        st.session_state.processor_api_hash = current_hash
            
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=google_api_key
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store = None
    
    def _get_api_key_hash(self, api_key: str) -> str:
        """Generate a hash of the API key for tracking"""
        if not api_key:
            return ""
        return hashlib.md5(api_key.encode()).hexdigest()[:16]
    
    def _cleanup_old_data(self):
        """Clean up old vector store data when account changes"""
        try:
            data_dir = "./data"
            if os.path.exists(data_dir):
                for item in os.listdir(data_dir):
                    if item.startswith("chroma_db_"):
                        item_path = os.path.join(data_dir, item)
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                            print(f"[DEBUG] Cleaned up old vector store: {item}")
        except Exception as e:
            print(f"[DEBUG] Warning: Could not clean up old data: {e}")
        
        self.vector_store = None
        
        cleanup_keys = ['documents_processed', 'processing_results', 'current_files']
        for key in cleanup_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        print("[DEBUG] Document processor data cleaned for account change")
        
    def process_pdfs(self, uploaded_files) -> Dict[str, Any]:
        """Procesa los PDFs subidos y los vectoriza"""
        if self.vector_store:
            try:
                self.vector_store.delete_collection()
            except:
                pass
        self.vector_store = None
        
        all_documents = []
        file_summaries = {}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f'Procesando {uploaded_file.name}...')
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                loader = PyPDFLoader(tmp_file_path)
                documents = loader.load()
                
                for doc in documents:
                    doc.metadata['source_file'] = uploaded_file.name
                    doc.metadata['file_index'] = i
                
                chunks = self.text_splitter.split_documents(documents)
                all_documents.extend(chunks)
                
                file_summaries[uploaded_file.name] = {
                    'pages': len(documents),
                    'chunks': len(chunks),
                    'size': len(uploaded_file.getvalue())
                }
                
            finally:
                os.unlink(tmp_file_path)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.text('Creando índice vectorial...')
        import time
        account_hash = st.session_state.get('processor_api_hash', 'unknown')
        unique_dir = f"./data/chroma_db_{account_hash}_{int(time.time())}"
        
        try:
            self.vector_store = Chroma.from_documents(
                documents=all_documents,
                embedding=self.embeddings,
                persist_directory=unique_dir
            )
            print(f"[DEBUG] Vector store created for account: {account_hash}")
        except Exception as e:
            st.error(f"Error creando índice vectorial: {e}")
            st.info("Verifica que tu GOOGLE_API_KEY tenga permisos para embeddings")
            raise e
        
        status_text.text('Procesamiento completado!')
        progress_bar.empty()
        status_text.empty()
        
        return {
            'total_documents': len(all_documents),
            'file_summaries': file_summaries,
            'vector_store': self.vector_store
        }
    
    def get_relevant_documents(self, query: str, k: int = 4) -> List[Document]:
        """Obtiene documentos relevantes para una consulta"""
        if not self.vector_store:
            return []
        
        return self.vector_store.similarity_search(query, k=k)
