"""
Main FastAPI Application for Voice AI Agent with RAG
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import init_db
from health.routes import router as health_router
from documents.routes import router as documents_router
from prompt.routes import router as prompt_router
from livekit_auth.routes import router as livekit_router
from rag.routes import router as rag_router

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

# CORS middleware - configure via CORS_ORIGINS env var (comma-separated)
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_db()


# Register routers
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(prompt_router)
app.include_router(livekit_router)
app.include_router(rag_router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
