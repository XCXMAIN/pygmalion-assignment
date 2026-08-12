import logging
import uuid

from app.core.embeddings import create_embedding
from app.core.llm import extract_memory
from app.db.session import AsyncSessionLocal
from app.models.memory import Memory

logger = logging.getLogger(__name__)


async def process_memory_extraction(
    character_id: uuid.UUID, user_message: str, assistant_message: str
) -> None:
    """Background task: extract a memory from one conversation turn and store it."""
    try:
        result = await extract_memory(user_message, assistant_message)

        if not result.should_remember or not result.memory:
            return

        embedding = await create_embedding(result.memory)

        async with AsyncSessionLocal() as db:
            db.add(
                Memory(
                    character_id=character_id,
                    text=result.memory,
                    embedding=embedding,
                    memory_type=result.type,
                    emotion=result.emotion,
                    importance=result.importance if result.importance is not None else 0.5,
                )
            )
            await db.commit()
    except Exception:
        logger.exception("Memory extraction failed for character_id=%s", character_id)
