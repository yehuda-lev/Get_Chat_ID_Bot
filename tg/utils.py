import logging
import asyncio

import httpx
from pyrogram import types, Client, raw

from db import repository, tables
from locales.translation_manager import manager, TranslationKeys


_logger = logging.getLogger(__name__)


def create_stats(type_stats: tables.StatsType, lang: str):
    """Create stats"""

    asyncio.create_task(
        repository.create_stats(type_stats=type_stats, language_code=lang),
    )


list_langs = [
    "en",
    "he",
    "ar",
    "ru",
    "zh-hans",
    "hi",
    "es",
    "fr",
]


async def set_bot_info(client: Client, langs: list[str]):
    """
    Set name, bio and description for the bot
    """
    for text_lang in langs:
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


async def set_bot_commands(client: Client, langs: list[str]):
    """
    Set commands for the bot
    """
    for text_lang in langs:
        if text_lang == "en":
            lang = ""  # default language
        else:
            lang = text_lang

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


async def paste_rs(code: str) -> tuple[bool, str]:
    """
    Paste code to paste.rs
    """
    url = "https://paste.rs"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, content=code)
        if response.status_code == 201:  # Created
            return True, f"{response.text.strip()}.py3"
        return False, response.text


async def paste_kaizoku(code: str) -> tuple[bool, str]:
    """
    Paste code to paste.kaizoku.cyou
    """
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
    }
    url = "https://paste.kaizoku.cyou/api/v2/pastes"
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, headers=headers, json={"content": code})
        if response.status_code == 201:
            return True, f"https://paste.kaizoku.cyou/{response.json()['id']}"
        else:
            return False, response.text


async def pate_code(code: str) -> str:
    paste = await paste_kaizoku(code)
    if paste[0]:
        return paste[1]
    else:
        paste = await paste_rs(code)
        if paste[0]:
            return paste[1]
        else:
            return paste[1]
