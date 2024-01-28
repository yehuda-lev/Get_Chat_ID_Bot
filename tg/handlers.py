from pyrogram import handlers, filters

from tg import filters as tg_filters, get_ids, admin_command


def regex_start(arg: str):
    return filters.regex(rf"^/start ({arg})")


HANDLERS = [
    handlers.MessageHandler(
        get_ids.choice_lang,
        filters.text
        & (filters.command("lang") | regex_start(arg="lang"))
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_me,
        filters.text
        & (filters.command("me") | regex_start(arg="me"))
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_chats_manager,
        filters.text
        & (filters.command("admin") | regex_start(arg="admin"))
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.welcome,
        filters.text
        & filters.command("start")
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_username,
        filters.text
        & filters.private
        & filters.create(tg_filters.is_username)
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_forward,
        filters.forwarded
        & filters.private
        & (
            filters.all & ~filters.media_group
            | filters.create(tg_filters.is_media_group_exists)
        )
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_contact,
        filters.contact
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        admin_command.get_stats,
        filters.text
        & filters.command("stats")
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_admin)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        admin_command.get_message_for_subscribe,
        filters.private
        & (
            filters.text & filters.command("send")
            | filters.reply & filters.create(tg_filters.is_force_reply)
        )
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_admin)
        & filters.create(tg_filters.is_not_raw)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.CallbackQueryHandler(
        get_ids.get_lang,
        filters.create(tg_filters.create_user)
        & filters.create(tg_filters.query_lang)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.CallbackQueryHandler(
        admin_command.send_message,
        filters.create(lambda _, __, cbd: cbd.data.startswith("send"))
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_admin)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_request_peer,
        filters.private
        & filters.requested_chats
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_story,
        filters=filters.private
        & filters.story
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.RawUpdateHandler(get_ids.get_raw),
]
