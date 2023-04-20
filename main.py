from pyrogram import Client
import json

from tg.handlers import HANDLERS


def main():
    configFile = open("config.json")
    config = json.load(configFile)

    app = Client(config["clientName"], api_id=config["apiId"], api_hash=config["apiHash"],
                 bot_token=config["botToken"],)

    configFile.close()

    print(f"Bot {app.name} is up and running!")

    for handler in HANDLERS:
        app.add_handler(handler)

    app.run()


if __name__ == '__main__':
    main()

