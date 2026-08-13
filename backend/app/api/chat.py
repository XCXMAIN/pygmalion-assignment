import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.embeddings import create_embedding
from app.core.llm import generate_reply
from app.core.prompts import build_system_prompt, is_user_disengaged
from app.db.session import get_db
from app.models.character import Character
from app.models.message import Message
from app.schemas.message import ChatRequest, ChatResponse, MessageRead
from app.services.memory import process_memory_extraction, search_memories

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

    query_embedding = await create_embedding(payload.message)
    memories = await search_memories(db, character_id, query_embedding)

    recent_user_messages = [m.content for m in recent_messages if m.role == "user"]
    recent_user_messages.append(payload.message)
    user_disengaged = is_user_disengaged(recent_user_messages)

    # 관계 단계가 바뀐 뒤 캐릭터가 아직 한 번도 응답하지 않았다면 "막 전환된 직후"로 본다.
    stage_just_changed = False
    if character.stage_changed_at is not None:
        reply_since_change = await db.execute(
            select(Message.message_id)
            .where(
                Message.character_id == character_id,
                Message.role == "assistant",
                Message.created_at > character.stage_changed_at,
            )
            .limit(1)
        )
        stage_just_changed = reply_since_change.scalar_one_or_none() is None

    system_prompt = build_system_prompt(character, memories, user_disengaged, stage_just_changed)
    history = [{"role": m.role, "content": m.content} for m in recent_messages]
    history.append({"role": "user", "content": payload.message})

    reply_segments = await generate_reply(system_prompt, history)

    # 세그먼트를 같은 트랜잭션에서 저장하면 DB의 now()가 동일해질 수 있어 순서가
    # 보장되지 않으므로, 밀리초 단위로 증가하는 timestamp를 직접 부여한다.
    now = datetime.now(timezone.utc)
    db.add(Message(character_id=character_id, role="user", content=payload.message, created_at=now))
    db.add_all(
        [
            Message(
                character_id=character_id,
                role="assistant",
                content=segment,
                created_at=now + timedelta(milliseconds=i + 1),
            )
            for i, segment in enumerate(reply_segments)
        ]
    )
    await db.commit()

    reply_text_for_extraction = " ".join(reply_segments)
    background_tasks.add_task(
        process_memory_extraction, character_id, payload.message, reply_text_for_extraction
    )

    return ChatResponse(messages=reply_segments, relationship_stage=character.relationship_stage)
