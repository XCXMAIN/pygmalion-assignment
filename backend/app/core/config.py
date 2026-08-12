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

    # 최근 대화 컨텍스트로 포함할 메시지 개수 (user+assistant 합산, 약 10턴)
    RECENT_CONTEXT_MESSAGES: int = 20


settings = Settings()
