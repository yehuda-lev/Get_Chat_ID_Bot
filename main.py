from pyrogram import Client, __version__
from pyrogram.raw.all import layer

from tg.handlers import HANDLERS
from db import filters as db_filters
from data import utils


settings = utils.get_settings()


class Bot(Client):
    name = settings.PYROGRAM_NAME_SESSION

    def __init__(self):
        super().__init__(
            name=self.name,
            api_id=settings.TELEGRAM_API_ID,
            api_hash=settings.TELEGRAM_API_HASH,
            bot_token=settings.TELEGRAM_BOT_TOKEN,
        )

    async def start(self):
        await super().start()

        me = await self.get_me()
        print(
            f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{me.username}."
        )


def main():
    app = Bot()

    for handler in HANDLERS:
        app.add_handler(handler)

    app.run()


if __name__ == "__main__":
    for admin in settings.ADMINS.split(","):
        if not db_filters.is_user_exists(tg_id=int(admin)):
            db_filters.create_user(tg_id=int(admin), name="admin", admin=True)
        else:
            db_filters.change_admin(tg_id=int(admin), admin=True)

    main()
