"""
LiveKit Agent: Orchestrates STT → LLM → TTS pipeline with RAG

This is the core voice agent that:
1. Listens to user speech (STT - Speech-to-Text)
2. Retrieves relevant context from documents (RAG via backend API)
3. Generates response using LLM with context
4. Speaks response back (TTS - Text-to-Speech)
"""
import os
import logging
from dotenv import load_dotenv
import httpx

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai, silero

load_dotenv()
logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


async def _fetch_rag_context(user_msg: str) -> str:
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


async def _before_llm_cb(agent: VoicePipelineAgent, chat_ctx: llm.ChatContext):
    """
    Called before every LLM invocation.
    Injects RAG context from the latest user message into the chat context.
    """
    # Find the last user message
    user_msg = ""
    for msg in reversed(chat_ctx.messages):
        if msg.role == "user" and msg.content:
            user_msg = msg.content
            break

    if user_msg:
        context = await _fetch_rag_context(user_msg)
        if context:
            # Insert a system message with RAG context right before the last user message
            rag_msg = llm.ChatMessage.create(
                role="system",
                text=f"Use the following document context to answer the user's question:\n\n{context}",
            )
            # Insert before the final user message
            chat_ctx.messages.insert(-1, rag_msg)

    return agent.llm.chat(chat_ctx=chat_ctx, fnc_ctx=agent.fnc_ctx)


async def entrypoint(ctx: JobContext):
    """Main entrypoint for LiveKit agent."""
    logger.info("Starting voice agent")

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for a user participant to join
    participant = await ctx.wait_for_participant()
    logger.info(f"Participant joined: {participant.identity}")

    # Fetch system prompt from backend
    system_prompt = (
        "You are a helpful AI assistant. "
        "Use the provided context from documents to answer questions accurately. "
        "If the answer is not in the context, say so clearly."
    )
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{BACKEND_URL}/prompt")
            if resp.status_code == 200:
                system_prompt = resp.json().get("system_prompt", system_prompt)
    except Exception as e:
        logger.warning(f"Could not fetch prompt from backend, using default: {e}")

    initial_ctx = llm.ChatContext()
    initial_ctx.append(role="system", text=system_prompt)

    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=openai.STT(model=os.getenv("STT_MODEL", "gpt-4o-transcribe")),
        llm=openai.LLM(model=os.getenv("LLM_MODEL", "gpt-4o")),
        tts=openai.TTS(
            model=os.getenv("TTS_MODEL", "gpt-4o-mini-tts"),
            voice=os.getenv("TTS_VOICE", "ash"),
        ),
        chat_ctx=initial_ctx,
        before_llm_cb=_before_llm_cb,
    )

    agent.start(ctx.room, participant)
    logger.info("Voice agent started and ready")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint),
    )
