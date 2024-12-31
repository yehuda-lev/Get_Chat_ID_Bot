import logging
from pyrogram import Client

from data import config

_logger = logging.getLogger(__name__)

settings = config.get_settings()

bot_1 = Client(
    name="my_bot",
    api_id=settings.telegram_api_id,
    api_hash=settings.telegram_api_hash,
    bot_token=settings.telegram_bot_token,
)

bot_2 = Client(
    name="my_bot_2",
    api_id=settings.telegram_api_id,
    api_hash=settings.telegram_api_hash,
    bot_token=settings.telegram_bot_token_2,
)
