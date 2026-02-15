"""
TTS (Text-to-Speech) Service Component
"""
import os
import logging
from dotenv import load_dotenv
from livekit.plugins import openai

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o-mini-tts"
DEFAULT_VOICE = "ash"


def create_tts() -> openai.TTS:
    model = os.getenv("TTS_MODEL", DEFAULT_MODEL)
    voice = os.getenv("TTS_VOICE", DEFAULT_VOICE)
    logger.info(f"Initializing TTS service with model: {model}, voice: {voice}")
    return openai.TTS(model=model, voice=voice)
