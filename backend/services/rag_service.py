"""
RAG Service using Local Embeddings (no OpenAI client issues)
"""
import os
import logging
from typing import List, Dict, Any
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class RAGService:
    """RAG Service using Local HuggingFace Embeddings"""
    
    def __init__(self):
        """Initialize RAG service"""
        
        # Use local embeddings
        logger.info("Loading local embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Initialize ChromaDB vector store
        persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        
        try:
            self.vector_store = Chroma(
                collection_name="documents",
                embedding_function=self.embeddings,
                persist_directory=persist_directory
            )
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            self.vector_store = None
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(os.getenv("CHUNK_SIZE", 1000)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 200)),
            length_function=len,
        )
    
    async def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents to the vector store"""
        if self.vector_store is None:
            raise Exception("Vector store not initialized")
        
        try:
            self.vector_store.add_texts(
                texts=texts,
                metadatas=metadatas
            )
            logger.info(f"Added {len(texts)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    async def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Retrieve relevant documents"""
        if self.vector_store is None:
            raise Exception("Vector store not initialized")
        
        if top_k is None:
            top_k = int(os.getenv("TOP_K_RESULTS", 3))
        
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=top_k
            )
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            logger.info(f"Retrieved {len(formatted_results)} documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    async def delete_by_source(self, filename: str):
        """Delete all chunks belonging to a source document from the vector store."""
        if self.vector_store is None:
            raise Exception("Vector store not initialized")

        try:
            collection = self.vector_store._collection
            results = collection.get(where={"source": filename})
            ids = results.get("ids", [])
            if ids:
                collection.delete(ids=ids)
                logger.info(f"Deleted {len(ids)} chunks for source: {filename}")
            else:
                logger.info(f"No chunks found for source: {filename}")
        except Exception as e:
            logger.error(f"Error deleting chunks for {filename}: {e}")
            raise

    def create_chunks(self, text: str) -> List[str]:
        """Split text into chunks"""
        chunks = self.text_splitter.split_text(text)
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    async def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """Get formatted context string for LLM"""
        results = await self.retrieve(query, top_k)
        
        if not results:
            return "No relevant documents found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result["metadata"].get("source", "Unknown")
            content = result["content"]
            context_parts.append(f"[Document {i}: {source}]\n{content}\n")
        
        context = "\n".join(context_parts)
        logger.info(f"Generated context from {len(results)} documents")
        return context
