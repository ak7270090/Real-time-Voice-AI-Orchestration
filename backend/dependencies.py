from documents.service import DocumentService
from rag.service import RAGService
from database import get_setting, upsert_setting

document_service = None
rag_service = None


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


async def get_current_prompt() -> str:
    return await get_setting("system_prompt", "")


async def update_current_prompt(prompt: str):
    await upsert_setting("system_prompt", prompt)
