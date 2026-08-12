import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.embeddings import create_embedding
from app.core.llm import extract_memory
from app.db.session import AsyncSessionLocal
from app.models.memory import Memory

logger = logging.getLogger(__name__)


async def search_memories(
    db: AsyncSession, character_id: uuid.UUID, query_embedding: list[float]
) -> list[Memory]:
    """캐릭터의 Memory를 코사인 유사도로 검색한다 (fact/event 구분 없이 함께 검색)."""
    distance = Memory.embedding.cosine_distance(query_embedding)
    max_distance = 1 - settings.MEMORY_SEARCH_SIMILARITY_THRESHOLD

    result = await db.execute(
        select(Memory)
        .where(Memory.character_id == character_id)
        .where(distance <= max_distance)
        .order_by(distance)
        .limit(settings.MEMORY_SEARCH_TOP_K)
    )
    return list(result.scalars().all())


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
                    entities=result.entities,
                )
            )
            await db.commit()
    except Exception:
        logger.exception("Memory extraction failed for character_id=%s", character_id)
