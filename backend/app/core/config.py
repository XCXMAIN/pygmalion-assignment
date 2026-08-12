from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "AI Lover Service"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql+asyncpg://pygmalion:pygmalion@localhost:5433/pygmalion"

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # 최근 대화 컨텍스트로 포함할 메시지 개수 (user+assistant 합산, 약 10턴)
    RECENT_CONTEXT_MESSAGES: int = 20

    # Memory RAG 검색 설정
    # text-embedding-3-small은 짧은 한국어 문장 간 코사인 유사도가 0.7까지 잘 오르지 않아
    # (관련 있는 쌍도 실측 0.4~0.5대) 0.3으로 보정. Top-K가 2차 안전장치 역할을 함.
    MEMORY_SEARCH_TOP_K: int = 5
    MEMORY_SEARCH_SIMILARITY_THRESHOLD: float = 0.3


settings = Settings()
