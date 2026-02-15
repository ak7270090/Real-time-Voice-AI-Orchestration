from pydantic import BaseModel


class PromptUpdate(BaseModel):
    system_prompt: str


class TokenRequest(BaseModel):
    room_name: str
    participant_name: str


class DocumentInfo(BaseModel):
    filename: str
    upload_time: str
    chunk_count: int
    file_size: int


class HealthResponse(BaseModel):
    status: str
    services: dict


class QueryRequest(BaseModel):
    query: str
