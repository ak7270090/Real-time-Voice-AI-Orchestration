from pydantic import BaseModel


class DocumentInfo(BaseModel):
    filename: str
    upload_time: str
    chunk_count: int
    file_size: int
