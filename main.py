import logging
import asyncio

import schedule
from pyrogram import raw, __version__, idle

from tg import handlers, others
from db import repository
from data import config, clients


config.setup_logging()
_logger = logging.getLogger(__name__)
settings = config.get_settings()


def schedule_jobs():
    """
    Schedule all the jobs that need to run periodically.
    """

    # Schedule update users last message every hour
    schedule.every(1).hour.do(
        lambda: asyncio.create_task(
            others.UserLastMessage.update_db_users_last_message()
        )
    )


async def schedule_jobs_async():
    """
    Run the scheduled jobs in an asynchronous loop.
    """

    schedule_jobs()

    while True:
        schedule.run_pending()

        await asyncio.sleep(1)


async def start_telegram_bot():
    logging.info(
        f"The bot is up and running on Pyrogram v{__version__} (Layer {raw.all.layer})."
    )

    for handler in handlers.HANDLERS:
        clients.bot_1.add_handler(handler)

    await clients.bot_1.start()
    await clients.bot_2.start()

    await idle()

    await clients.bot_1.stop()
    await clients.bot_2.stop()


async def main():
    # create admins
    for admin in settings.admins:
        if not (user := await repository.get_user(tg_id=admin)):
            await repository.create_user(
                tg_id=admin, name="admin", admin=True, language_code="he"
            )
        else:
            if not user.admin:
                await repository.update_user(tg_id=admin, admin=True)

    asyncio.create_task(schedule_jobs_async())
    await start_telegram_bot()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
    except KeyboardInterrupt:
        pass
