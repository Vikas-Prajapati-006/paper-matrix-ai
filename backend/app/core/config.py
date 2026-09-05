from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "PaperMatrix AI Backend"
    API_V1_STR: str = "/api/v1"
    
    # LLM Settings (Groq)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    
    # Redis Quota & Atomic Limiter Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    FREE_CREDITS_PER_DEVICE: int = 3
    CREDIT_WINDOW_SECONDS: int = 86400  # 24 Hours
    
    # Security & File Limits
    ADMIN_SECRET_KEY: str = "development_secret_key"
    MAX_FILE_SIZE_MB: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()