from pyrogram import handlers, filters

from tg import filters as tg_filters, get_ids, admin_command, help

HANDLERS = [
    handlers.MessageHandler(
        get_ids.get_forward,
        filters.forwarded
        & filters.private
        & (
                filters.all & ~filters.media_group
                | filters.create(tg_filters.is_media_group_exists)
        )
        & filters.create(tg_filters.create_user)
        & ~ filters.create(tg_filters.status_answer())
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.choice_lang,
        filters.text
        & tg_filters.start_command(command="lang")
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_me,
        filters.text
        & filters.private
        & tg_filters.start_command(command="me")
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_chats_manager,
        filters.text
        & tg_filters.start_command(command="admin")
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.welcome,
        filters.text
        & tg_filters.start_command(command="start")
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.added_to_group,
        filters.text
        & tg_filters.start_command(command="add")
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_ids_in_the_group,
        filters.text
        & tg_filters.start_command(command="id")
        & filters.group
    ),
    handlers.MessageHandler(
        help.handle_callback_data_help,
        filters.text
        & tg_filters.start_command(command="help")
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_about,
        filters.text
        & tg_filters.start_command(command="about")
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_username,
        filters.text
        & filters.private
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_username)
        & ~ filters.create(tg_filters.status_answer())
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_contact,
        filters.contact
        & filters.private
        & filters.create(tg_filters.create_user)
        & ~ filters.create(tg_filters.status_answer(answer=True))
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_request_peer,
        filters.private
        # & filters.requested_chats
        & filters.create(lambda _, __, msg: msg.chat_shared is not None or msg.users_shared is not None)
        & filters.create(tg_filters.create_user)
        & ~ filters.create(tg_filters.status_answer())
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.MessageHandler(
        get_ids.get_story,
        filters.private
        # & filters.story
        & filters.create(lambda _, __, msg: msg.story is not None)
        & filters.create(tg_filters.create_user)
        & ~ filters.create(tg_filters.status_answer())
        & filters.create(tg_filters.is_user_spamming),
    ),
    # admin command
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
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_admin)
        & (
                tg_filters.start_command(command="send")
                & ~ filters.create(tg_filters.status_answer()) |
                filters.create(tg_filters.status_answer(send_message_to_subscribers=True))
        )
    ),

    handlers.ChatMemberUpdatedHandler(
        get_ids.on_remove_permission,
        # filters.admin
    ),

    # callback
    handlers.CallbackQueryHandler(
        help.handle_callback_data_help,
        filters.create(lambda _, __, cbd: cbd.data.startswith("help"))
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.CallbackQueryHandler(
        get_ids.get_lang,
        filters.create(tg_filters.create_user)
        & filters.create(tg_filters.query_lang)
        & filters.create(tg_filters.is_user_spamming),
    ),
    handlers.CallbackQueryHandler(
        admin_command.send_message_to_subscribers,
        filters.create(lambda _, __, cbd: cbd.data.startswith("send"))
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_admin)
        & filters.create(tg_filters.is_user_spamming),
    ),

    handlers.RawUpdateHandler(get_ids.get_raw),
]
