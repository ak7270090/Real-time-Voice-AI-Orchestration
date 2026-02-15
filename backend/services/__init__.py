"""
Services package — separate pipeline components for the voice AI agent.

Components:
    stt_service     — Speech-to-Text (OpenAI Whisper)
    llm_service     — Large Language Model + RAG context injection
    tts_service     — Text-to-Speech (OpenAI TTS)
    rag_service     — Knowledge Base: vector store retrieval
    document_service — Document ingestion & processing
"""

from services.stt_service import create_stt
from services.tts_service import create_tts
from services.llm_service import create_llm, fetch_system_prompt, before_llm_cb, fetch_rag_context
from services.rag_service import RAGService
from services.document_service import DocumentService
