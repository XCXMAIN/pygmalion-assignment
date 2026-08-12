import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.llm import generate_reply
from app.core.prompts import build_system_prompt
from app.db.session import get_db
from app.models.character import Character
from app.models.message import Message
from app.schemas.message import ChatRequest, ChatResponse, MessageRead
from app.services.memory import process_memory_extraction

router = APIRouter(tags=["chat"])


@router.get("/characters/{character_id}/messages", response_model=list[MessageRead])
async def list_messages(
    character_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.character_id == character_id)
        .order_by(Message.created_at)
    )
    return list(result.scalars().all())


@router.post("/characters/{character_id}/chat", response_model=ChatResponse)
async def chat(
    character_id: uuid.UUID,
    payload: ChatRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    character = await db.get(Character, character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")

    result = await db.execute(
        select(Message)
        .where(Message.character_id == character_id)
        .order_by(Message.created_at.desc())
        .limit(settings.RECENT_CONTEXT_MESSAGES)
    )
    recent_messages = list(reversed(result.scalars().all()))

    system_prompt = build_system_prompt(character)
    history = [{"role": m.role, "content": m.content} for m in recent_messages]
    history.append({"role": "user", "content": payload.message})

    reply_text = await generate_reply(system_prompt, history)

    db.add_all(
        [
            Message(character_id=character_id, role="user", content=payload.message),
            Message(character_id=character_id, role="assistant", content=reply_text),
        ]
    )
    await db.commit()

    background_tasks.add_task(
        process_memory_extraction, character_id, payload.message, reply_text
    )

    return ChatResponse(message=reply_text, relationship_stage=character.relationship_stage)
