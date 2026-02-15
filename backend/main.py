"""
Main FastAPI Application for Voice AI Agent with RAG
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from settings import CORS_ORIGINS, BACKEND_PORT, LOG_LEVEL
from documents.routes import router as documents_router
from prompt.routes import router as prompt_router
from livekit_auth.routes import router as livekit_router
from rag.routes import router as rag_router
from health.routes import router as health_router
from observability.metrics_route import router as metrics_router
from observability import setup_logging, ObservabilityMiddleware

# Configure structured JSON logging
setup_logging(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Voice AI Agent API",
    description="Real-time voice agent with RAG capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Observability middleware (request ID, metrics, access logging)
app.add_middleware(ObservabilityMiddleware)

@app.on_event("startup")
async def startup():
    await init_db()


# Register routers
app.include_router(documents_router)
app.include_router(prompt_router)
app.include_router(livekit_router)
app.include_router(rag_router)
app.include_router(health_router)
app.include_router(metrics_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=BACKEND_PORT)
