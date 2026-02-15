import logging
from fastapi import APIRouter, HTTPException
from schemas import PromptUpdate
from dependencies import current_prompt

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/prompt")
async def get_prompt():
    """Get current system prompt"""
    return current_prompt


@router.post("/prompt")
async def update_prompt(prompt_update: PromptUpdate):
    """Update system prompt for the agent"""
    try:
        current_prompt["system_prompt"] = prompt_update.system_prompt
        logger.info(f"Prompt updated: {prompt_update.system_prompt[:50]}...")
        return {
            "message": "Prompt updated successfully",
            "prompt": current_prompt["system_prompt"]
        }
    except Exception as e:
        logger.error(f"Error updating prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
