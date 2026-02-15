from services.document_service import DocumentService
from services.rag_service import RAGService

document_service = None
rag_service = None

# Global state for agent prompt
current_prompt = {
    "system_prompt": "You are a helpful AI assistant. Use the provided context from documents to answer questions accurately and concisely."
}


def get_document_service():
    global document_service
    if document_service is None:
        document_service = DocumentService()
    return document_service


def get_rag_service():
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service
