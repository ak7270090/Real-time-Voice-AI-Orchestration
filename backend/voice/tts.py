"""
TTS (Text-to-Speech) Service Component
"""
import logging
from livekit.plugins import openai
from settings import TTS_MODEL, TTS_VOICE

logger = logging.getLogger(__name__)


def create_tts() -> openai.TTS:
    logger.info(f"Initializing TTS service with model: {TTS_MODEL}, voice: {TTS_VOICE}")
    return openai.TTS(model=TTS_MODEL, voice=TTS_VOICE)
