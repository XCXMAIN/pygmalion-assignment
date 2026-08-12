from typing import Literal

from pydantic import BaseModel, Field


class MemoryExtractionResult(BaseModel):
    should_remember: bool
    memory: str | None = Field(default=None, description="기억할 내용을 유저 시점 3인칭으로 서술한 문장")
    type: Literal["fact", "event"] | None = None
    emotion: str | None = Field(default=None, description="관련된 감정 (예: nervous, happy, tired)")
    importance: float | None = Field(default=None, ge=0, le=1)
