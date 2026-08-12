import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    message: str
    relationship_stage: str


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message_id: uuid.UUID
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
