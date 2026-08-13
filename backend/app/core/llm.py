from openai import AsyncOpenAI

from app.core.config import settings
from app.core.prompts import (
    EVOLVED_TRAITS_SYSTEM_PROMPT,
    MEMORY_EXTRACTION_SYSTEM_PROMPT,
    MESSAGE_SPLIT_INSTRUCTION,
)
from app.schemas.memory import MemoryExtractionResult
from app.schemas.message import ChatReplySegments

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_reply(system_prompt: str, history: list[dict[str, str]]) -> list[str]:
    completion = await _client.beta.chat.completions.parse(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": MESSAGE_SPLIT_INSTRUCTION},
            *history,
        ],
        response_format=ChatReplySegments,
        temperature=0.9,
        max_tokens=400,
    )
    segments = [s.strip() for s in completion.choices[0].message.parsed.messages if s and s.strip()]
    return segments[:3] if segments else [completion.choices[0].message.content or ""]


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
    return completion.choices[0].message.parsed


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
