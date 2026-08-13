import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.memory import Memory
from app.schemas.memory import MemoryRead

router = APIRouter(tags=["memories"])


@router.get("/characters/{character_id}/memories", response_model=list[MemoryRead])
async def list_memories(
    character_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[Memory]:
    result = await db.execute(
        select(Memory)
        .where(Memory.character_id == character_id)
        .order_by(Memory.timestamp.desc())
    )
    return list(result.scalars().all())
