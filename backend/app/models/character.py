import uuid
from datetime import datetime

from sqlalchemy import ARRAY, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Character(Base):
    __tablename__ = "characters"

    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    name: Mapped[str] = mapped_column(String(50))
    personality_tags: Mapped[list[str]] = mapped_column(ARRAY(String))
    relationship_type: Mapped[str] = mapped_column(String(50))
    relationship_stage: Mapped[str] = mapped_column(String(20), default="stranger")
    speech_style: Mapped[dict] = mapped_column(JSONB)
    custom_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    evolved_traits: Mapped[str | None] = mapped_column(Text, nullable=True)
    stage_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
