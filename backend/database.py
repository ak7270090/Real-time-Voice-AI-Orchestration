"""
SQLite database for persistent storage of document metadata and settings.
"""
import aiosqlite
import logging
from constants import DEFAULT_SYSTEM_PROMPT
from settings import DB_PATH

logger = logging.getLogger(__name__)


async def init_db():
    """Create tables and seed defaults."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                upload_time TEXT NOT NULL,
                chunk_count INTEGER NOT NULL,
                file_size INTEGER NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        # Seed default system prompt if not present
        cursor = await db.execute(
            "SELECT value FROM settings WHERE key = ?", ("system_prompt",)
        )
        row = await cursor.fetchone()
        if row is None:
            await db.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                ("system_prompt", DEFAULT_SYSTEM_PROMPT),
            )
        await db.commit()
    logger.info("Database initialized")


# ── Document CRUD ──────────────────────────────────────────────


async def insert_document(filename: str, upload_time: str, chunk_count: int, file_size: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO documents (filename, upload_time, chunk_count, file_size) VALUES (?, ?, ?, ?)",
            (filename, upload_time, chunk_count, file_size),
        )
        await db.commit()


async def list_documents():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT filename, upload_time, chunk_count, file_size FROM documents")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def delete_document(filename: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM documents WHERE filename = ?", (filename,))
        await db.commit()


# ── Settings CRUD ──────────────────────────────────────────────


async def get_setting(key: str, default: str = "") -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row[0] if row else default


async def upsert_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
            (key, value, value),
        )
        await db.commit()
