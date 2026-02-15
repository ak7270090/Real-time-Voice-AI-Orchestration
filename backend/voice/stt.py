"""
STT (Speech-to-Text) Service Component
"""
import logging
from livekit.plugins import openai
from settings import STT_MODEL

logger = logging.getLogger(__name__)


def create_stt() -> openai.STT:
    logger.info(f"Initializing STT service with model: {STT_MODEL}")
    return openai.STT(model=STT_MODEL)
