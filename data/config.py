from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """read the settings from .env file"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    telegram_api_id: int
    telegram_api_hash: str
    telegram_bot_token: str
    telegram_bot_token_2: str
    admins: list[int]
    limit_spam: int
    admin_to_update_of_payment: int


@lru_cache
def get_settings() -> Settings:
    """get the settings from .env file"""
    return Settings()
