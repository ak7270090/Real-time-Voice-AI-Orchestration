import os
import logging
from fastapi import APIRouter, HTTPException
from livekit import api
from schemas import TokenRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate-token")
async def generate_token(request: TokenRequest):
    """
    Generate LiveKit access token for joining a room

    This token allows the frontend to connect to LiveKit
    and participate in the voice conversation
    """
    try:
        livekit_url = os.getenv("LIVEKIT_URL")
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")

        if not all([livekit_url, api_key, api_secret]):
            raise HTTPException(
                status_code=500,
                detail="LiveKit credentials not configured"
            )

        token = api.AccessToken(api_key, api_secret)
        token.with_identity(request.participant_name)
        token.with_name(request.participant_name)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=request.room_name,
        ))

        jwt_token = token.to_jwt()

        logger.info(f"Generated token for {request.participant_name} in room {request.room_name}")

        return {
            "token": jwt_token,
            "url": livekit_url,
            "room_name": request.room_name
        }

    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
