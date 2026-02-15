"""
LiveKit Voice Agent Orchestrator

Wires together the separate pipeline components:
  1. STT  (services.stt_service)      — Speech-to-Text
  2. LLM  (services.llm_service)      — Language Model + RAG context injection
  3. TTS  (services.tts_service)      — Text-to-Speech
  4. KB   (services.rag_service)      — Knowledge Base ingestion + retrieval

The agent connects to a LiveKit room and runs the voice pipeline
for each participant.
"""
import logging
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import silero

from observability.logging_config import setup_logging
from settings import LOG_LEVEL

setup_logging(level=LOG_LEVEL)

from voice import create_stt, create_llm, create_tts, fetch_system_prompt, before_llm_cb

logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext):
    """Main entrypoint for LiveKit agent."""
    logger.info("Starting voice agent")

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()
    logger.info(f"Participant joined: {participant.identity}")

    # --- Build pipeline from separate components ---
    system_prompt = await fetch_system_prompt()

    initial_ctx = llm.ChatContext()
    initial_ctx.append(role="system", text=system_prompt)

    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=create_stt(),           # 1. STT component
        llm=create_llm(),           # 2. LLM component
        tts=create_tts(),           # 3. TTS component
        chat_ctx=initial_ctx,
        before_llm_cb=before_llm_cb,  # 4. KB/RAG injection
    )

    agent.start(ctx.room, participant)
    logger.info("Voice agent started and ready")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint),
    )
