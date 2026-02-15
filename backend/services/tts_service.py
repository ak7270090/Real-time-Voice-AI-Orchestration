"""
TTS (Text-to-Speech) Service Component

Configures and provides the text-to-speech component for the voice pipeline.
Uses OpenAI's TTS models for speech synthesis.
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
    """
    Create and return a configured TTS instance.

    Environment variables:
        TTS_MODEL: OpenAI TTS model name (default: gpt-4o-mini-tts)
        TTS_VOICE: Voice to use (default: ash)
    """
    model = os.getenv("TTS_MODEL", DEFAULT_MODEL)
    voice = os.getenv("TTS_VOICE", DEFAULT_VOICE)
    logger.info(f"Initializing TTS service with model: {model}, voice: {voice}")
    return openai.TTS(model=model, voice=voice)
