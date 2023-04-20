from pyrogram import Client
import json

from tg.handlers import HANDLERS
from db import filters as db_filters

configFile = open("config.json")
config = json.load(configFile)


def main():
    app = Client(config["clientName"], api_id=config["apiId"], api_hash=config["apiHash"],
                 bot_token=config["botToken"],)

    configFile.close()

    print(f"Bot {app.name} is up and running!")

    for handler in HANDLERS:
        app.add_handler(handler)

    app.run()


if __name__ == '__main__':
    for admin in config["admins"].split(','):
        if not db_filters.is_user_exists(tg_id=admin):
            db_filters.create_user(tg_id=admin, name='admin', admin=True)
        else:
            db_filters.change_admin(tg_id=admin, admin=True)

    main()

