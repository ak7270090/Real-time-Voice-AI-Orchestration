import os
import tempfile
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from schemas import DocumentInfo
from dependencies import get_document_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document for RAG

    This endpoint:
    1. Saves the uploaded file
    2. Extracts text from the document
    3. Chunks the text into smaller pieces
    4. Creates embeddings for each chunk
    5. Stores in vector database for retrieval
    """
    try:
        logger.info(f"Uploading document: {file.filename}")

        if not file.filename.endswith(('.pdf', '.txt')):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and TXT files are supported"
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            doc_service = get_document_service()
            result = await doc_service.process_document(
                file_path=tmp_file_path,
                filename=file.filename
            )

            logger.info(f"Document processed: {file.filename}, {result['chunks_created']} chunks")

            return {
                "message": "Document uploaded and processed successfully",
                **result
            }
        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """Get list of all uploaded documents"""
    try:
        doc_service = get_document_service()
        documents = doc_service.list_documents()
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document from the knowledge base"""
    try:
        doc_service = get_document_service()
        await doc_service.delete_document(filename)
        return {"message": f"Document {filename} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
