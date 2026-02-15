"""
Document Service
Handles document upload and processing
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from rag_service import RAGService

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for processing and managing documents"""
    
    def __init__(self):
        """Initialize document service"""
        self.rag_service = RAGService()
        self.documents_metadata = []  # Track uploaded documents
    
    async def process_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Process a document and add to knowledge base
        
        Args:
            file_path: Path to the document file
            filename: Original filename
            
        Returns:
            Dict with processing results
        """
        try:
            # Extract text based on file type
            if filename.endswith('.pdf'):
                text = self._extract_pdf_text(file_path)
            elif filename.endswith('.txt'):
                text = self._extract_txt_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {filename}")
            
            # Create chunks
            chunks = self.rag_service.create_chunks(text)
            
            # Create metadata for each chunk
            metadatas = []
            for i, chunk in enumerate(chunks):
                metadatas.append({
                    "source": filename,
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                })
            
            # Add to vector store
            await self.rag_service.add_documents(chunks, metadatas)
            
            # Track document
            file_size = os.path.getsize(file_path)
            self.documents_metadata.append({
                "filename": filename,
                "upload_time": datetime.utcnow().isoformat(),
                "chunk_count": len(chunks),
                "file_size": file_size
            })
            
            logger.info(f"Processed document: {filename}, {len(chunks)} chunks")
            
            return {
                "filename": filename,
                "chunks_created": len(chunks),
                "file_size": file_size
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            raise
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF"""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all uploaded documents"""
        return self.documents_metadata
