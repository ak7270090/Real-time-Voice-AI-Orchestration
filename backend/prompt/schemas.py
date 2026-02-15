from pydantic import BaseModel


class PromptUpdate(BaseModel):
    system_prompt: str
