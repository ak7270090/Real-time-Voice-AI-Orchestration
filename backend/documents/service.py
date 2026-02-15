"""
Document Service — handles document upload and processing.
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from rag.service import RAGService
from database import insert_document, list_documents as db_list_documents, delete_document as db_delete_document

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for processing and managing documents"""

    def __init__(self):
        self.rag_service = RAGService()

    async def process_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        try:
            if filename.endswith('.pdf'):
                text = self._extract_pdf_text(file_path)
            elif filename.endswith('.txt'):
                text = self._extract_txt_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {filename}")

            chunks = self.rag_service.create_chunks(text)

            metadatas = []
            for i, chunk in enumerate(chunks):
                metadatas.append({
                    "source": filename,
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                })

            await self.rag_service.add_documents(chunks, metadatas)

            file_size = os.path.getsize(file_path)
            await insert_document(
                filename=filename,
                upload_time=datetime.utcnow().isoformat(),
                chunk_count=len(chunks),
                file_size=file_size,
            )

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
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    def _extract_txt_text(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    async def list_documents(self) -> List[Dict[str, Any]]:
        return await db_list_documents()

    async def delete_document(self, filename: str):
        await self.rag_service.delete_by_source(filename)
        await db_delete_document(filename)
