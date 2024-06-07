import logging
from logging.handlers import RotatingFileHandler
from pyrogram import Client, raw, __version__

from tg.handlers import HANDLERS
from db import repository
from data import config


# log config
logging.getLogger("pyrogram").setLevel(logging.WARNING)

root_logger = logging.getLogger()
root_logger.setLevel(level=logging.DEBUG)

log_format = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)
root_logger.addHandler(console_handler)

file_handler = RotatingFileHandler(
    filename="bot.log", maxBytes=20 * (2**20), backupCount=3, mode="D", encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)
root_logger.addHandler(file_handler)


_logger = logging.getLogger(__name__)

settings = config.get_settings()


app = Client(
    name="my_bot",
    api_id=settings.telegram_api_id,
    api_hash=settings.telegram_api_hash,
    bot_token=settings.telegram_bot_token,
)


def main():
    logging.info(
        f"The bot is up and running on Pyrogram v{__version__} (Layer {raw.all.layer})."
    )

    for handler in HANDLERS:
        app.add_handler(handler)

    for admin in settings.admins:
        if not repository.is_user_exists(tg_id=admin):
            repository.create_user(
                tg_id=admin, name="admin", admin=True, language_code="he"
            )
        else:
            if not repository.is_admin(tg_id=admin):
                repository.update_user(tg_id=admin, admin=True)

    app.run()


if __name__ == "__main__":
    main()
