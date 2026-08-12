from openai import AsyncOpenAI

from app.core.config import settings
from app.core.prompts import MEMORY_EXTRACTION_SYSTEM_PROMPT
from app.schemas.memory import MemoryExtractionResult

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_reply(system_prompt: str, history: list[dict[str, str]]) -> str:
    response = await _client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[{"role": "system", "content": system_prompt}, *history],
        temperature=0.9,
        max_tokens=400,
    )
    return response.choices[0].message.content


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
