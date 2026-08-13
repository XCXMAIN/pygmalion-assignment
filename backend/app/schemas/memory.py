import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MemoryExtractionResult(BaseModel):
    should_remember: bool
    memory: str | None = Field(
        default=None,
        description="유저 시점 3인칭 사실 서술 ('유저는 ~다'), 20~40자 내외 한 문장. 감정 뉘앙스는 넣지 않음",
    )
    type: Literal["fact", "event"] | None = None
    emotion: str | None = Field(default=None, description="관련된 감정 (예: nervous, happy, tired)")
    importance: float | None = Field(default=None, ge=0, le=1)
    entities: list[str] | None = Field(
        default=None, description="memory에서 뽑은 핵심 키워드 1~3개"
    )


class MemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    memory_id: uuid.UUID
    text: str
    memory_type: Literal["fact", "event"]
    emotion: str | None
    importance: float
    entities: list[str] | None
    timestamp: datetime
