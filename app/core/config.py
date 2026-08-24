from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite+aiosqlite:///./supplymind.db"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "development-secret-change-me"
    access_token_minutes: int = 60
    ai_provider: str = "local"
    ai_model: str = "deterministic"
    auto_seed: bool = True

settings = Settings()
