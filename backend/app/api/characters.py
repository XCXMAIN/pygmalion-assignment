import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterRead

router = APIRouter(tags=["characters"])


@router.post("/characters", response_model=CharacterRead, status_code=201)
async def create_character(
    payload: CharacterCreate, db: AsyncSession = Depends(get_db)
) -> Character:
    character = Character(
        user_id=payload.user_id,
        name=payload.name,
        personality_tags=payload.personality_tags,
        relationship_type=payload.relationship_type,
        speech_style=payload.speech_style.model_dump(),
        custom_description=payload.custom_description,
    )
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return character


@router.get("/characters", response_model=list[CharacterRead])
async def list_characters(
    user_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[Character]:
    result = await db.execute(
        select(Character)
        .where(Character.user_id == user_id)
        .order_by(Character.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/characters/{character_id}", response_model=CharacterRead)
async def get_character(
    character_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> Character:
    character = await db.get(Character, character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character
