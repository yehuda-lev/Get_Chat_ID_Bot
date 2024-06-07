import os
from typing import Type
import dotenv


dotenv.load_dotenv()


class Settings:
    """read the settings from .env file"""

    PYROGRAM_NAME_SESSION = os.environ["PYROGRAM_NAME_SESSION"]
    TELEGRAM_API_ID = os.environ["TELEGRAM_API_ID"]
    TELEGRAM_API_HASH = os.environ["TELEGRAM_API_HASH"]
    TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
    ADMINS = os.environ["ADMINS"]
    LIMIT_SPAM = os.environ["LIMIT_SPAM"]


def get_settings() -> Type[Settings]:
    """get the settings from .env file"""
    return Settings
