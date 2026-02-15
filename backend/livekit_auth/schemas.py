from pydantic import BaseModel


class TokenRequest(BaseModel):
    room_name: str
    participant_name: str
