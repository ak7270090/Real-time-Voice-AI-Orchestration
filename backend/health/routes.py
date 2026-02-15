"""
Health check endpoint — probes SQLite and ChromaDB.
"""
import time
import logging

import aiosqlite
from fastapi import APIRouter

from settings import DB_PATH

logger = logging.getLogger(__name__)

router = APIRouter()


async def check_sqlite() -> dict:
    try:
        start = time.perf_counter()
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("SELECT 1")
        return {"status": "ok", "latency_ms": round((time.perf_counter() - start) * 1000, 2)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_chromadb() -> dict:
    try:
        from dependencies import get_rag_service
        rag = get_rag_service()
        if rag.vector_store is None:
            return {"status": "error", "error": "vector store not initialized"}
        count = rag.vector_store._collection.count()
        return {"status": "ok", "document_count": count}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/health")
async def health_check():
    sqlite_status = await check_sqlite()
    chroma_status = check_chromadb()

    checks = {
        "sqlite": sqlite_status,
        "chromadb": chroma_status,
    }

    all_ok = all(c["status"] == "ok" for c in checks.values())

    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
    }
