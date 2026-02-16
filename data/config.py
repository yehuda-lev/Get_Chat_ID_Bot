import logging
import sys
from functools import lru_cache
from logging.handlers import RotatingFileHandler

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


def setup_logging():
    """
    Setup logging configuration
    """
    logger_levels = {
        "pyrogram": logging.WARNING,
        "urllib3": logging.WARNING,
        "httpx": logging.WARNING,
        "httpcore": logging.WARNING,
        "watchfiles": logging.WARNING,
        "asyncio": logging.WARNING,
        "schedule": logging.WARNING,
        "aiosqlite": logging.WARNING,
    }

    for logger_name, level in logger_levels.items():
        logging.getLogger(logger_name).setLevel(level)

    log_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level=logging.DEBUG)

    # log config
    logging_handlers = [
        (
            logging.StreamHandler(),
            logging.INFO,
        ),
        (
            RotatingFileHandler(
                filename="log.log",
                maxBytes=20 * 1024 * 1024,  # 20 MB
                backupCount=3,
                mode="a",
                encoding="utf-8",
            ),
            logging.DEBUG,
        ),
    ]
    for handler, level in logging_handlers:
        handler.setLevel(level)
        handler.setFormatter(log_format)
        root_logger.addHandler(handler)

    # write uncaught exceptions to log file
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        root_logger.critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception
