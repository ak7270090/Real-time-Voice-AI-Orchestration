"""
Application-wide constants — static values that don't change per environment.
"""

# ── File upload ───────────────────────────────────────────────
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_FILE_EXTENSIONS = (".pdf", ".txt")

# ── RAG / Vector store ───────────────────────────────────────
CHROMA_COLLECTION_NAME = "documents"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 100
DEFAULT_TOP_K_RESULTS = 3

# ── Database ──────────────────────────────────────────────────
DEFAULT_DB_PATH = "app.db"

# ── Default system prompt (single source of truth) ───────────
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant. "
    "Use the provided context from documents to answer questions accurately. "
    "If the answer is not in the context, say so clearly."
)
