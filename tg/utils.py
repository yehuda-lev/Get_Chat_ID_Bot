import logging
import asyncio

import httpx
from pyrogram import types, Client, raw

from data import clients
from db import repository, tables
from locales.translation_manager import manager, TranslationKeys


_logger = logging.getLogger(__name__)


def get_buttons(
    chat_id: int | None,
    name: str | None,
    lang: str,
    user: repository.User | None = None,
    inline_buttons: list[list[types.InlineKeyboardButton] | None] = None,
    reply_markup: types.InlineKeyboardMarkup | None = None,
    by: str | None = None,
) -> types.InlineKeyboardMarkup | None:
    if chat_id is None:
        return (
            None
            if not inline_buttons and not reply_markup
            else reply_markup or types.InlineKeyboardMarkup(inline_buttons)
        )

    if user:
        copy_button = None
        if not user.feature:
            asyncio.create_task(send_alert_to_change_settings(user=user))
            copy_button = True

        if copy_button or user.feature.copy_button:  # if user has copy button feature
            if not inline_buttons:
                inline_buttons = []
            inline_buttons.append(
                [
                    types.InlineKeyboardButton(
                        text=name,
                        copy_text=types.CopyTextButton(text=str(chat_id)),
                    )
                ]
            )

    return types.InlineKeyboardMarkup(
        [
            *(inline_buttons if inline_buttons else []),
            [
                types.InlineKeyboardButton(
                    text=(
                        manager.get_translation(TranslationKeys.BUTTON_GET_LINK, lang)
                        if not by
                        else "Powered by 'Get Chat ID Bot' 🪪"
                    ),
                    url=f"https://t.me/{clients.bot_1.me.username}?start={f'link_{chat_id}' if not by else f'start_{by}'}",
                )
            ],
        ]
    )


async def send_alert_to_change_settings(user: repository.User):
    """
    Send alert to user to change settings
    """
    tg_id = user.tg_id
    lang = user.lang

    await repository.create_feature(user_id=tg_id)

    # wait for user receive the CopyButton
    await asyncio.sleep(1)

    await clients.bot_1.send_message(
        chat_id=tg_id,
        text="Change your settings if the message is not supported",
    )


async def send_link_to_chat_by_id(_: Client, msg: types.Message):
    """Send link to chat by id"""
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang

    try:
        _, chat_id = msg.text.split(" ", 1)

        if chat_id.startswith("link_"):
            chat_id = chat_id[5:]
    except ValueError:
        await msg.reply(manager.get_translation(TranslationKeys.FORMAT_LINK, lang))
        return

    is_group, link, link_android, link_ios = None, None, None, None
    if chat_id.startswith("-100"):  # supergroup or channel
        link = f"https://t.me/c/{chat_id[4:]}/1{''.join('0' for _ in range(7))}"
        is_group = True
    elif chat_id.startswith("-"):  # group
        link = f"https://t.me/{chat_id[1:]}/1{''.join('0' for _ in range(7))}"
        is_group = True
    else:
        chat_id = chat_id.replace(" ", "")
        is_group = False
        link_android = f"tg://openmessage?user_id={chat_id}"
        link_ios = f"tg://user?id={chat_id}"

    if is_group:
        buttons = [
            types.InlineKeyboardButton(
                text="Link 🔗",
                url=link,
            )
        ]
    else:
        buttons = [
            types.InlineKeyboardButton(
                text="Android 📱",
                url=link_android,
            ),
            types.InlineKeyboardButton(
                text="iOS 🔗",
                url=link_ios,
            ),
        ]

    await msg.reply(
        text=manager.get_translation(TranslationKeys.LINK_TO_CHAT, lang).format(
            chat_id
        ),
        reply_markup=types.InlineKeyboardMarkup([buttons]),
        quote=True,
    )

    create_stats(type_stats=tables.StatsType.LINK, lang=msg.from_user.language_code)


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
