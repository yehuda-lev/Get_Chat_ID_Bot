import logging
import asyncio
from pyrogram import raw, __version__, idle

from tg import handlers
from db import repository
from data import config, clients


config.setup_logging()
_logger = logging.getLogger(__name__)
settings = config.get_settings()


async def main():
    logging.info(
        f"The bot is up and running on Pyrogram v{__version__} (Layer {raw.all.layer})."
    )

    for handler in handlers.HANDLERS:
        clients.bot_1.add_handler(handler)

    for admin in settings.admins:
        if not (user := await repository.get_user(tg_id=admin)):
            await repository.create_user(
                tg_id=admin, name="admin", admin=True, language_code="he"
            )
        else:
            if not user.admin:
                await repository.update_user(tg_id=admin, admin=True)

    await clients.bot_1.start()
    await clients.bot_2.start()

    await idle()

    await clients.bot_1.stop()
    await clients.bot_2.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
