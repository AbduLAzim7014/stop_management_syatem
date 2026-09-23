from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart Shop AI"
    database_url: str = "sqlite:///./smart_shop.db"
    ai_provider: str = "demo"
    ai_api_key: str | None = None
    ai_model: str = "gpt-4o-mini"
    ai_base_url: str = "https://api.openai.com/v1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
