from pyrogram import Client

from tg.handlers import HANDLERS
from db import filters as db_filters


import os
from dotenv import load_dotenv

load_dotenv()


def main():
    app = Client(name=os.environ['PYROGRAM_NAME_SESSION'], api_id=os.environ['TELEGRAM_API_ID'],
                 api_hash=os.environ['TELEGRAM_API_HASH'], bot_token=os.environ['TELEGRAM_BOT_TOKEN'])

    print(f"Bot {app.name} is up and running!")

    for handler in HANDLERS:
        app.add_handler(handler)

    app.run()


if __name__ == '__main__':
    for admin in os.environ['ADMINS'].split(','):
        if not db_filters.is_user_exists(tg_id=int(admin)):
            db_filters.create_user(tg_id=int(admin), name='admin', admin=True)
        else:
            db_filters.change_admin(tg_id=int(admin), admin=True)

    main()

