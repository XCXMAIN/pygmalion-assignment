import logging

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.prompts import (
    EVOLVED_TRAITS_SYSTEM_PROMPT,
    MEMORY_EXTRACTION_SYSTEM_PROMPT,
    MESSAGE_SPLIT_INSTRUCTION,
)
from app.schemas.memory import MemoryExtractionResult
from app.schemas.message import ChatReplySegments

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_reply(system_prompt: str, history: list[dict[str, str]]) -> list[str]:
    completion = await _client.beta.chat.completions.parse(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[
            # 출력 형식(세그먼트 분할) 지침을 먼저 두고, 대화 내용/톤을 결정하는 페르소나
            # 지침(질문·공감 비율 포함)을 history 바로 앞에 둬서 우선순위가 흐려지지 않게 한다.
            {"role": "system", "content": MESSAGE_SPLIT_INSTRUCTION},
            {"role": "system", "content": system_prompt},
            *history,
        ],
        response_format=ChatReplySegments,
        temperature=0.9,
        max_tokens=400,
    )
    message = completion.choices[0].message
    # 히스토리가 길어질수록(실측 20턴 안팎에서 최대 ~50%) parsed가 None으로 오는 경우가 늘어난다.
    # 이때 message.refusal에 실제로 정상적인 대화 텍스트가 담겨 오는 것을 확인했다 (안전 관련
    # 거부가 아님 — OpenAI structured output의 알려진 신뢰성 이슈로 보임). content → refusal
    # 순으로 폴백해서, 값이 있는데도 의미 없는 플레이스홀더가 나가는 일이 없도록 한다.
    if message.parsed is not None:
        segments = [s.strip() for s in message.parsed.messages if s and s.strip()]
    else:
        logger.warning("generate_reply: structured output parsed=None, history_len=%d, falling back", len(history))
        fallback_text = message.content or getattr(message, "refusal", None) or ""
        segments = [fallback_text.strip()] if fallback_text.strip() else []
    return segments[:3] if segments else ["음... 잠깐만."]


async def extract_memory(user_message: str, assistant_message: str) -> MemoryExtractionResult:
    completion = await _client.beta.chat.completions.parse(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": MEMORY_EXTRACTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"유저: {user_message}\n캐릭터: {assistant_message}",
            },
        ],
        response_format=MemoryExtractionResult,
    )
    parsed = completion.choices[0].message.parsed
    # generate_reply와 동일한 이유로 parsed가 None일 수 있다. 이 경우 안전하게 기억하지 않음으로 처리.
    if parsed is None:
        logger.warning("extract_memory: structured output parsed=None, falling back to should_remember=False")
        return MemoryExtractionResult(should_remember=False)
    return parsed


async def generate_evolved_traits(
    personality_tags: list[str], existing_traits: str | None, facts: list[str]
) -> str:
    fact_lines = "\n".join(f"- {f}" for f in facts)
    user_content = (
        f"원본 성격: {', '.join(personality_tags)}\n"
        f"기존 특성 요약: {existing_traits or '(아직 없음)'}\n"
        f"지금까지 이 유저에 대해 쌓인 fact:\n{fact_lines}"
    )
    response = await _client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": EVOLVED_TRAITS_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.7,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()
