"""Retrieval-Augmented Generation engine for medical guideline processing."""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class RAGEngine:
    """Production-grade RAG engine for medical guideline retrieval and processing."""
    
    def __init__(self, load_documents: bool = False):
        """Initialize the RAG engine with vector store and embeddings."""
        self.guidelines_path = "assets/guidelines"
        self.vector_db_path = os.getenv('VECTOR_DB_PATH', 'data/chroma_db')
        self.vector_store = None
        self.embeddings = None
        
        self._initialize_embeddings()
        
        if load_documents:
            logger.info("♻️  Force reload requested. Re-indexing documents...")
            self._initialize_vector_store()
            self.load_pdf_guidelines()
        else:
            if self._vector_store_exists():
                logger.info("📂 Loading existing vector store from disk...")
                self._initialize_vector_store()
                self._check_vector_store_status()
            else:
                logger.warning("⚠️  Vector store not found. Creating new one...")
                self._initialize_vector_store()
                self.load_pdf_guidelines()
    
    def _vector_store_exists(self) -> bool:
        """Check if the vector database directory exists and is not empty."""
        if not os.path.exists(self.vector_db_path):
            return False
        return any(os.scandir(self.vector_db_path))

    def _initialize_embeddings(self) -> None:
        """Initialize Ollama embeddings for document vectorization."""
        try:
            from langchain_ollama import OllamaEmbeddings
            
            logger.info("Initializing Ollama embeddings...")
            self.embeddings = OllamaEmbeddings(model="llama3")
            logger.info("Embeddings initialized successfully")
            
        except ImportError:
            logger.error("langchain_ollama not installed. Install with: pip install langchain-ollama")
            self.embeddings = None
        except Exception as e:
            logger.error(f"Embeddings initialization error: {e}")
            self.embeddings = None
    
    def _initialize_vector_store(self) -> None:
        """Initialize LangChain Chroma vector store."""
        try:
            if self.embeddings is None:
                logger.warning("Embeddings not available. Vector store initialization skipped")
                return
                
            from langchain_chroma import Chroma
            
            logger.info(f"Initializing vector store at: {self.vector_db_path}")
            
            self.vector_store = Chroma(
                collection_name="medical_guidelines",
                embedding_function=self.embeddings,
                persist_directory=self.vector_db_path
            )

            logger.info("Vector store connection established")
            
        except ImportError:
            logger.error("langchain-chroma not installed. Install with: pip install langchain-chroma")
            self.vector_store = None
        except Exception as e:
            logger.error(f"Vector store initialization error: {e}")
            self.vector_store = None
    
    def _check_vector_store_status(self) -> None:
        """Check if vector store has documents and report status."""
        try:
            if self.vector_store is None:
                return
            
            # Retrieve collection count safely
            count = self.vector_store._collection.count()
            logger.info(f"✓ Vector store ready with {count} documents")
                
        except Exception as e:
            logger.debug(f"Could not check vector store count: {e}")
            logger.info("Vector store initialized")

    def _get_category_from_filename(self, filename: str) -> str:
        """Assign disease category based on filename."""
        fname = filename.lower()
        if "diabetes" in fname: return "diabetes"
        if "hypertension" in fname or "blood_pressure" in fname: return "hypertension"
        if "anemia" in fname or "iron" in fname: return "anaemia"
        if "pcos" in fname: return "pcos"
        if "obesity" in fname or "esi" in fname: return "obesity"
        if "dietary_guidelines" in fname or "icmr" in fname: return "general"
        if "pregnancy" in fname: return "pregnancy"
        return "general"

    def load_pdf_guidelines(self) -> bool:
        """
        Load and process PDF files into vector store with SMART METADATA TAGGING.
        """
        if Load and process PDF files into vector store with metadata tagging.    logger.info(f"Created guidelines directory: {self.guidelines_path}")
        
        pdf_files = list(Path(self.guidelines_path).glob("*.pdf"))
        
        if not pdf_files:
            logger.info(f"No PDFs found in {self.guidelines_path}")
            return False
        
        try:
            from langchain_community.document_loaders import PyMuPDFLoader
            
            all_documents = []
            
            for pdf_file in pdf_files:
                logger.info(f"Processing PDF: {pdf_file.name}")
                loader = PyMuPDFLoader(str(pdf_file))
                documents = loader.load()
                
                # --- UPGRADED METADATA TAGGING ---
                category = self._get_category_from_filename(pdf_file.name)
                category = self._get_category_from_filename(pdf_file.name)
                logger.info(f"  s:
                    doc.metadata["source"] = pdf_file.name
                    doc.metadata["category"] = category  
                
                all_documents.extend(documents)
            
            if all_documents:
                self._process_and_store_documents(all_documents)
                return True
            else:
                logger.warning("No content extracted from PDFs")
                return False
        
        except ImportError:
            logger.error("langchain_community not installed. Install with: pip install langchain-community")
            return False
        except Exception as e:
            logger.error(f"Error loading PDFs: {e}")
            return False
    
    def _process_and_store_documents(self, documents: List) -> None:
        """
        Process documents through text splitting and store in vector database.
        """
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            
            logger.info("Starting document processing pipeline...")
            
            # Optimized chunking for Medical Text (Context preservation)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
            )
            
            logger.info("Splitting documents into chunks...")
            split_docs = text_splitter.split_documents(documents)
            logger.info(f"Generated {len(split_docs)} document chunks")
            
            if self.vector_store is not None:
                # Optional: Reset DB if doing a full reload (prevents duplicates)
                # self.vector_store.delete_collection() 
                logger.info("Documents successfully stored in vector database")
            else:
                logger.warning("Vector store not available. Documents not stored")
                
        except ImportError:
            logger.error("langchain-text-splitters missing.")
        except Exception as e:
            logger.error(f"Document processing error: {e}")
    
    def retrieve_context(self, query: str, max_results: int = 4) -> Tuple[str, List]:
        """
        Retrieve relevant documents from vector store using similarity search.
        
        IMPROVEMENT: Since we added 'category' metadata, the semantic search
        will now naturally prioritize documents that align with the disease terms
        in Retrieve relevant documents from vector store using similarity search."""
        if self.vector_store is None:
            logger.warning("Vector store not available.")
            return self._get_default_guidance(query), []
        
        try:
            if not retrieved_docs:
                return self._get_default_guidance(query), []
            
            # Format context with source citation
            serialized_context = "\n\n".join(
                f"[Source: {doc.metadata.get('source', 'Unknown')} | Tag: {doc.metadata.get('category', 'General')}]\n{doc.page_content}"
                for doc in retrieved_docs
            )
            
            return serialized_context, retrieved_docs
            
        except Exception as e:
            logger.error(f"Context retrieval error: {e}")
            return self._get_default_guidance(query), []
    
    def _get_default_guidance(self, query: str) -> str:
        """Prn "Please refer to standard medical guidelines."


# --- SINGLETON INSTANCE MANAGEMENT ---

_rag_instance = None

def get_rag_engine(load_documents: bool = False) -> RAGEngine:
    """
    Get or create RAGEngine instance (singleton pattern).
    """
    global _rag_instance
    
    if _rag_instance is not None:
        if load_documents:
            logger.info("🔄 Reload requested on existing engine.")
            _rag_instance.load_pdf_guidelines()
    logger.info("✨ Creating new RAGEngine instance...")
    _rag_instance = RAGEngine(load_documents=load_documents)
    return _rag_instance

def retrieve_context(query: str, max_results: int = 4) -> Tuple[str, List]:
    """Convenience function to retrieve context."""
    engine = get_rag_engine(load_documents=False)
    return engine.retrieve_context(query, max_results)