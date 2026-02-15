"""
Environment-dependent settings — reads from env vars with sensible defaults.
"""
import os
from dotenv import load_dotenv
from constants import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_TOP_K_RESULTS,
    DEFAULT_DB_PATH,
)

load_dotenv()

# ── Voice pipeline models ────────────────────────────────────
STT_MODEL = os.getenv("STT_MODEL", "gpt-4o-transcribe")
TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")
TTS_VOICE = os.getenv("TTS_VOICE", "ash")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")

# ── Backend networking ───────────────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8000))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")

# ── ChromaDB ─────────────────────────────────────────────────
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# ── RAG tuning ───────────────────────────────────────────────
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", DEFAULT_CHUNK_SIZE))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", DEFAULT_CHUNK_OVERLAP))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", DEFAULT_TOP_K_RESULTS))

# ── Database ─────────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB_PATH)

# ── HTTP timeouts (seconds) ──────────────────────────────────
HTTP_TIMEOUT_PROMPT = float(os.getenv("HTTP_TIMEOUT_PROMPT", 5.0))
HTTP_TIMEOUT_RAG = float(os.getenv("HTTP_TIMEOUT_RAG", 10.0))
