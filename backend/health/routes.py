import os
from fastapi import APIRouter
from health.schemas import HealthResponse
from dependencies import rag_service, get_current_prompt
from settings import HEALTH_STT_MODEL, HEALTH_LLM_MODEL, HEALTH_TTS_MODEL, HEALTH_TTS_VOICE

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
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


@router.get("/agent-config")
async def get_agent_config():
    """Get current agent configuration"""
    prompt = await get_current_prompt()
    return {
        "system_prompt": prompt,
        "stt_model": HEALTH_STT_MODEL,
        "llm_model": HEALTH_LLM_MODEL,
        "tts_model": HEALTH_TTS_MODEL,
        "tts_voice": HEALTH_TTS_VOICE,
    }
