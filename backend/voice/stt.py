"""
STT (Speech-to-Text) Service Component
"""
import os
import logging
from dotenv import load_dotenv
from livekit.plugins import openai

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o-transcribe"


def create_stt() -> openai.STT:
    model = os.getenv("STT_MODEL", DEFAULT_MODEL)
    logger.info(f"Initializing STT service with model: {model}")
    return openai.STT(model=model)
