"""
LLM (Large Language Model) Service Component

Handles system prompt fetching and RAG context injection.
"""
import logging
import httpx

from livekit.agents import llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai

from constants import DEFAULT_SYSTEM_PROMPT
from settings import LLM_MODEL, BACKEND_URL, HTTP_TIMEOUT_PROMPT, HTTP_TIMEOUT_RAG
from observability.metrics import metrics

logger = logging.getLogger(__name__)


def create_llm() -> openai.LLM:
    logger.info(f"Initializing LLM service with model: {LLM_MODEL}")
    return openai.LLM(model=LLM_MODEL)


async def fetch_system_prompt() -> str:
    """Fetch the system prompt from the backend API."""
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_PROMPT) as client:
            resp = await client.get(f"{BACKEND_URL}/prompt")
            if resp.status_code == 200:
                return resp.json().get("system_prompt", DEFAULT_SYSTEM_PROMPT)
    except Exception as e:
        logger.warning(f"Could not fetch prompt from backend, using default: {e}")
    return DEFAULT_SYSTEM_PROMPT


async def fetch_rag_context(user_msg: str) -> str:
    """Call backend /query endpoint to retrieve RAG context."""
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_RAG) as client:
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
        metrics.voice_rag_injections_total.labels(status="error").inc()
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
            metrics.voice_rag_injections_total.labels(status="success").inc()
            rag_msg = llm.ChatMessage.create(
                role="system",
                text=f"Use the following document context to answer the user's question:\n\n{context}",
            )
            chat_ctx.messages.insert(-1, rag_msg)
        else:
            metrics.voice_rag_injections_total.labels(status="empty").inc()

    return agent.llm.chat(chat_ctx=chat_ctx, fnc_ctx=agent.fnc_ctx)
