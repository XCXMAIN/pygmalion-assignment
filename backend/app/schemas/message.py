import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatReplySegments(BaseModel):
    messages: list[str] = Field(
        description="카톡처럼 순차적으로 보여줄 짧은 메시지 조각들 (보통 1~2개, 많아도 3개)"
    )


class ChatResponse(BaseModel):
    messages: list[str]
    relationship_stage: str


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message_id: uuid.UUID
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
