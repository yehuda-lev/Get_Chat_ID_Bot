import logging
import asyncio

from pyrogram import types, Client, raw

from db import repository, tables
from locales.translation_manager import manager, TranslationKeys


_logger = logging.getLogger(__name__)


def create_stats(type_stats: tables.StatsType, lang: str):
    """Create stats"""

    asyncio.create_task(
        repository.create_stats(type_stats=type_stats, lang=lang),
    )


async def set_bot_info(client: Client):
    """
    Set name and bio, description and commands for the bot
    """
    list_langs = [
        # "en",
        # "he",
        # "ar",
        # "ru",
        "zh-hans"
    ]
    for text_lang in list_langs:
        if text_lang == "en":
            lang = ""  # default language
        else:
            lang = text_lang

        await client.invoke(
            raw.functions.bots.SetBotInfo(
                lang_code=lang,
                name=manager.get_translation(TranslationKeys.BOT_NAME, text_lang),
                about=manager.get_translation(
                    TranslationKeys.BOT_ABOUT, text_lang
                ),  # outside the chat, 120 characters
                description=manager.get_translation(
                    TranslationKeys.BOT_DESCRIPTION, text_lang
                ),  # inside the chat, 512 characters
            )
        )

        await asyncio.sleep(2)

        await client.set_bot_commands(
            commands=[
                types.BotCommand(
                    "start",
                    manager.get_translation(TranslationKeys.START_COMMAND, text_lang),
                ),
                types.BotCommand(
                    "lang",
                    manager.get_translation(TranslationKeys.LANG_COMMAND, text_lang),
                ),
                types.BotCommand(
                    "help",
                    manager.get_translation(TranslationKeys.HELP_COMMAND, text_lang),
                ),
                types.BotCommand(
                    "me", manager.get_translation(TranslationKeys.ME_COMMAND, text_lang)
                ),
                types.BotCommand(
                    "add",
                    manager.get_translation(TranslationKeys.ADD_COMMAND, text_lang),
                ),
                types.BotCommand(
                    "admin",
                    manager.get_translation(TranslationKeys.ADMIN_COMMAND, text_lang),
                ),
                types.BotCommand(
                    "about",
                    manager.get_translation(TranslationKeys.ABOUT_COMMAND, text_lang),
                ),
                types.BotCommand(
                    "link",
                    manager.get_translation(TranslationKeys.LINK_COMMAND, text_lang),
                ),
                types.BotCommand(
                    "search",
                    manager.get_translation(TranslationKeys.SEARCH_COMMAND, text_lang),
                ),
                types.BotCommand(
                    "donate",
                    manager.get_translation(TranslationKeys.DONATE_COMMAND, text_lang),
                ),
            ],
            language_code=lang,
            scope=types.BotCommandScopeAllPrivateChats(),
        )

        await asyncio.sleep(2)
