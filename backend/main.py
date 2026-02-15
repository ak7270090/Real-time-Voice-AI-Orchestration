"""
Main FastAPI Application for Voice AI Agent with RAG
"""
import os
import logging
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from livekit import api
import asyncio

from services.document_service import DocumentService
from services.rag_service import RAGService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Voice AI Agent API",
    description="Real-time voice agent with RAG capabilities",
    version="1.0.0"
)

# CORS middleware - configure for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services - lazy loaded to avoid import errors
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

# Global state for agent prompt
current_prompt = {
    "system_prompt": "You are a helpful AI assistant. Use the provided context from documents to answer questions accurately and concisely."
}


# Pydantic Models
class PromptUpdate(BaseModel):
    system_prompt: str


class TokenRequest(BaseModel):
    room_name: str
    participant_name: str


class DocumentInfo(BaseModel):
    filename: str
    upload_time: str
    chunk_count: int
    file_size: int


class HealthResponse(BaseModel):
    status: str
    services: dict


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check health of all services"""
    vector_db_status = "not_initialized"
    try:
        if rag_service is not None:
            vector_db_status = "connected" if rag_service.vector_store else "disconnected"
    except:
        pass
    
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "vector_db": vector_db_status,
            "livekit": "configured" if os.getenv("LIVEKIT_URL") else "not_configured"
        }
    }


# Document Management Endpoints
@app.post("/upload-document")
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
        
        # Validate file type
        if not file.filename.endswith(('.pdf', '.txt')):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and TXT files are supported"
            )
        
        # Save file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process document using file path
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
            # Clean up temp file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """Get list of all uploaded documents"""
    try:
        doc_service = get_document_service()
        documents = doc_service.list_documents()
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document from the knowledge base"""
    try:
        doc_service = get_document_service()
        await doc_service.delete_document(filename)
        # Note: Also need to remove from vector store
        # This is simplified - in production, track document IDs
        return {"message": f"Document {filename} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Prompt Management Endpoints
@app.get("/prompt")
async def get_prompt():
    """Get current system prompt"""
    return current_prompt


@app.post("/prompt")
async def update_prompt(prompt_update: PromptUpdate):
    """Update system prompt for the agent"""
    try:
        current_prompt["system_prompt"] = prompt_update.system_prompt
        logger.info(f"Prompt updated: {prompt_update.system_prompt[:50]}...")
        return {
            "message": "Prompt updated successfully",
            "prompt": current_prompt["system_prompt"]
        }
    except Exception as e:
        logger.error(f"Error updating prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# LiveKit Token Generation
@app.post("/generate-token")
async def generate_token(request: TokenRequest):
    """
    Generate LiveKit access token for joining a room
    
    This token allows the frontend to connect to LiveKit
    and participate in the voice conversation
    """
    try:
        # Get LiveKit credentials from environment
        livekit_url = os.getenv("LIVEKIT_URL")
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        if not all([livekit_url, api_key, api_secret]):
            raise HTTPException(
                status_code=500,
                detail="LiveKit credentials not configured"
            )
        
        # Create access token
        token = api.AccessToken(api_key, api_secret)
        token.with_identity(request.participant_name)
        token.with_name(request.participant_name)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=request.room_name,
        ))
        
        jwt_token = token.to_jwt()
        
        logger.info(f"Generated token for {request.participant_name} in room {request.room_name}")
        
        return {
            "token": jwt_token,
            "url": livekit_url,
            "room_name": request.room_name
        }
        
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# RAG Query Endpoint (for testing)
class QueryRequest(BaseModel):
    query: str


@app.post("/query")
async def query_rag(request: QueryRequest):
    """
    Test RAG retrieval without voice
    Useful for debugging and testing
    """
    try:
        rag = get_rag_service()
        results = await rag.retrieve(request.query, top_k=3)
        return {
            "query": request.query,
            "results": results
        }
    except Exception as e:
        logger.error(f"Error querying RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Get current agent configuration
@app.get("/agent-config")
async def get_agent_config():
    """Get current agent configuration"""
    return {
        "system_prompt": current_prompt["system_prompt"],
        "stt_model": os.getenv("STT_MODEL", "whisper-1"),
        "llm_model": os.getenv("LLM_MODEL", "gpt-4"),
        "tts_model": os.getenv("TTS_MODEL", "tts-1"),
        "tts_voice": os.getenv("TTS_VOICE", "alloy"),
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)