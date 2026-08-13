import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select

from app.core.llm import generate_evolved_traits
from app.db.session import AsyncSessionLocal
from app.models.character import Character
from app.models.memory import Memory
from app.models.message import Message

logger = logging.getLogger(__name__)

# 기획서 3장 stage_thresholds 그대로
STAGE_THRESHOLDS = {
    "acquaintance": {"turns": 6, "memories": 2},
    "close": {"turns": 15, "memories": 5},
    "lover": {"turns": 30, "memories": 9},
}


def _compute_stage(turns: int, memory_count: int) -> str:
    stage = "stranger"
    for candidate, threshold in STAGE_THRESHOLDS.items():
        if turns >= threshold["turns"] and memory_count >= threshold["memories"]:
            stage = candidate
    return stage


async def update_relationship_stage(character_id: uuid.UUID) -> None:
    """누적 대화 턴수 + Memory 개수 조건을 체크해 relationship_stage를 갱신한다."""
    try:
        async with AsyncSessionLocal() as db:
            character = await db.get(Character, character_id)
            if character is None:
                return

            turns = (
                await db.execute(
                    select(func.count())
                    .select_from(Message)
                    .where(Message.character_id == character_id, Message.role == "user")
                )
            ).scalar_one()
            memory_count = (
                await db.execute(
                    select(func.count())
                    .select_from(Memory)
                    .where(Memory.character_id == character_id)
                )
            ).scalar_one()

            new_stage = _compute_stage(turns, memory_count)
            if new_stage != character.relationship_stage:
                character.relationship_stage = new_stage
                character.stage_changed_at = datetime.now(timezone.utc)
                await db.commit()
    except Exception:
        logger.exception("Relationship stage update failed for character_id=%s", character_id)


async def maybe_update_evolved_traits(character_id: uuid.UUID) -> None:
    """fact Memory 개수가 3의 배수에 도달할 때마다 evolved_traits를 누적 계승 방식으로 갱신한다."""
    try:
        async with AsyncSessionLocal() as db:
            character = await db.get(Character, character_id)
            if character is None:
                return

            fact_result = await db.execute(
                select(Memory.text)
                .where(Memory.character_id == character_id, Memory.memory_type == "fact")
                .order_by(Memory.timestamp)
            )
            facts = [row[0] for row in fact_result.all()]

            if len(facts) == 0 or len(facts) % 3 != 0:
                return

            new_traits = await generate_evolved_traits(
                personality_tags=character.personality_tags,
                existing_traits=character.evolved_traits,
                facts=facts,
            )
            character.evolved_traits = new_traits
            await db.commit()
    except Exception:
        logger.exception("Evolved traits update failed for character_id=%s", character_id)
