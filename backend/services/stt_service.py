"""
STT (Speech-to-Text) Service Component

Configures and provides the speech-to-text component for the voice pipeline.
Uses OpenAI's Whisper/GPT-4o-transcribe for transcription.
"""
import os
import logging
from dotenv import load_dotenv
from livekit.plugins import openai

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o-transcribe"


def create_stt() -> openai.STT:
    """
    Create and return a configured STT instance.

    Environment variables:
        STT_MODEL: OpenAI STT model name (default: gpt-4o-transcribe)
    """
    model = os.getenv("STT_MODEL", DEFAULT_MODEL)
    logger.info(f"Initializing STT service with model: {model}")
    return openai.STT(model=model)
