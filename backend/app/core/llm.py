from openai import AsyncOpenAI

from app.core.config import settings

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_reply(system_prompt: str, history: list[dict[str, str]]) -> str:
    response = await _client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[{"role": "system", "content": system_prompt}, *history],
        temperature=0.9,
        max_tokens=400,
    )
    return response.choices[0].message.content
