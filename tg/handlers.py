from pyrogram import handlers, filters

from tg import filters as tg_filters
from tg.admin_command import get_stats, send_message, get_message_for_subscribe
from tg.get_ids import (
    choice_lang,
    get_me,
    get_chats_manager,
    welcome,
    forward,
    get_contact,
    get_lang,
    get_request_peer,
    get_story,
    get_raw,
)


def regex_start(arg: str):
    return filters.regex(rf"^/start ({arg})")


HANDLERS = [
    handlers.MessageHandler(
        choice_lang,
        filters.text
        & (filters.command("lang") | regex_start(arg="lang"))
        & filters.private
        & filters.create(tg_filters.create_user),
    ),
    handlers.MessageHandler(
        get_me,
        filters.text
        & (filters.command("me") | regex_start(arg="me"))
        & filters.private
        & filters.create(tg_filters.create_user),
    ),
    handlers.MessageHandler(
        get_chats_manager,
        filters.text
        & (filters.command("admin") | regex_start(arg="admin"))
        & filters.private
        & filters.create(tg_filters.create_user),
    ),
    handlers.MessageHandler(
        welcome,
        filters.text
        & filters.command("start")
        & filters.private
        & filters.create(tg_filters.create_user),
    ),
    handlers.MessageHandler(
        forward,
        filters.forwarded & filters.private & filters.create(tg_filters.create_user),
    ),
    handlers.MessageHandler(
        get_contact,
        filters.contact & filters.private & filters.create(tg_filters.create_user),
    ),
    handlers.MessageHandler(
        get_stats,
        filters.text
        & filters.command("stats")
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_admin),
    ),
    handlers.MessageHandler(
        get_message_for_subscribe,
        filters.private
        & (
            filters.text & filters.command("send")
            | filters.reply & filters.create(tg_filters.is_force_reply)
        )
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_admin)
        & filters.create(tg_filters.is_not_raw),
    ),
    handlers.CallbackQueryHandler(
        get_lang,
        filters.create(tg_filters.create_user) & filters.create(tg_filters.query_lang),
    ),
    handlers.CallbackQueryHandler(
        send_message,
        filters.create(lambda _, __, cbd: cbd.data.startswith("send"))
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_admin),
    ),
    handlers.MessageHandler(
        get_request_peer,
        filters=(
            filters.private
            & filters.requested_chats
            & filters.create(tg_filters.create_user)
        ),
    ),
    handlers.MessageHandler(
        get_story,
        filters=(
            filters.private & filters.story & filters.create(tg_filters.create_user)
        ),
    ),
    handlers.RawUpdateHandler(get_raw),
]
