from pyrogram import Client, __version__
from pyrogram.raw.all import layer

from tg.handlers import HANDLERS
from db import repository
from data import config


settings = config.get_settings()


class Bot(Client):
    name = settings.pyrogram_name_session

    def __init__(self):
        super().__init__(
            name=self.name,
            api_id=settings.telegram_api_id,
            api_hash=settings.telegram_api_hash,
            bot_token=settings.telegram_bot_token,
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
    for admin in settings.admins:
        if not repository.is_user_exists(tg_id=admin):
            repository.create_user(tg_id=admin, name="admin", admin=True)
        else:
            repository.change_admin(tg_id=admin, admin=True)

    main()
