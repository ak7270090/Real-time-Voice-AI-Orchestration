"""
LLM (Large Language Model) Service Component

Configures and provides the LLM component for the voice pipeline.
Handles system prompt fetching and RAG context injection.
"""
import os
import logging
from dotenv import load_dotenv
import httpx

from livekit.agents import llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant. "
    "Use the provided context from documents to answer questions accurately. "
    "If the answer is not in the context, say so clearly."
)


def create_llm() -> openai.LLM:
    """
    Create and return a configured LLM instance.

    Environment variables:
        LLM_MODEL: OpenAI LLM model name (default: gpt-4o)
    """
    model = os.getenv("LLM_MODEL", DEFAULT_MODEL)
    logger.info(f"Initializing LLM service with model: {model}")
    return openai.LLM(model=model)


async def fetch_system_prompt() -> str:
    """Fetch the system prompt from the backend API."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{BACKEND_URL}/prompt")
            if resp.status_code == 200:
                return resp.json().get("system_prompt", DEFAULT_SYSTEM_PROMPT)
    except Exception as e:
        logger.warning(f"Could not fetch prompt from backend, using default: {e}")
    return DEFAULT_SYSTEM_PROMPT


async def fetch_rag_context(user_msg: str) -> str:
    """Call backend /query endpoint to retrieve RAG context."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{BACKEND_URL}/query",
                json={"query": user_msg},
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if not results:
                return ""
            parts = []
            for i, r in enumerate(results, 1):
                source = r.get("metadata", {}).get("source", "Unknown")
                content = r.get("content", "")
                parts.append(f"[Document {i}: {source}]\n{content}")
            return "\n\n".join(parts)
    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}")
        return ""


async def before_llm_cb(agent: VoicePipelineAgent, chat_ctx: llm.ChatContext):
    """
    Called before every LLM invocation.
    Injects RAG context from the latest user message into the chat context.
    """
    user_msg = ""
    for msg in reversed(chat_ctx.messages):
        if msg.role == "user" and msg.content:
            user_msg = msg.content
            break

    if user_msg:
        context = await fetch_rag_context(user_msg)
        if context:
            rag_msg = llm.ChatMessage.create(
                role="system",
                text=f"Use the following document context to answer the user's question:\n\n{context}",
            )
            chat_ctx.messages.insert(-1, rag_msg)

    return agent.llm.chat(chat_ctx=chat_ctx, fnc_ctx=agent.fnc_ctx)
