"""
RAG Service using Local Embeddings (no OpenAI client issues)
"""
import logging
from typing import List, Dict, Any
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from constants import CHROMA_COLLECTION_NAME, EMBEDDING_MODEL_NAME, DEFAULT_TOP_K_RESULTS
from settings import CHROMA_PERSIST_DIR, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS

logger = logging.getLogger(__name__)


class RAGService:
    """RAG Service using Local HuggingFace Embeddings"""

    def __init__(self):
        logger.info("Loading local embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME
        )

        try:
            self.vector_store = Chroma(
                collection_name=CHROMA_COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=CHROMA_PERSIST_DIR
            )
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            self.vector_store = None

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )

    async def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        if self.vector_store is None:
            raise Exception("Vector store not initialized")

        try:
            self.vector_store.add_texts(texts=texts, metadatas=metadatas)
            logger.info(f"Added {len(texts)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    async def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        if self.vector_store is None:
            raise Exception("Vector store not initialized")

        if top_k is None:
            top_k = TOP_K_RESULTS

        try:
            results = self.vector_store.similarity_search_with_score(
                query=query, k=top_k
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
        chunks = self.text_splitter.split_text(text)
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks

    async def get_context_for_query(self, query: str, top_k: int = DEFAULT_TOP_K_RESULTS) -> str:
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
