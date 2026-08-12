from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
    has_vector = result.scalar_one_or_none() is not None
    return {"status": "ok", "pgvector_enabled": has_vector}
