import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SpeechStyle(BaseModel):
    formality: Literal["존댓말", "반말"]
    use_emoji: bool


class CharacterCreate(BaseModel):
    user_id: uuid.UUID
    name: str = Field(min_length=1, max_length=50)
    personality_tags: list[str] = Field(min_length=1, max_length=5)
    relationship_type: str = Field(min_length=1, max_length=50)
    speech_style: SpeechStyle
    custom_description: str | None = Field(default=None, max_length=1000)


class CharacterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    character_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    personality_tags: list[str]
    relationship_type: str
    relationship_stage: str
    speech_style: SpeechStyle
    custom_description: str | None
    created_at: datetime
