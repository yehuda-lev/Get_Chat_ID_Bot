from pyrogram import handlers, filters

from tg import filters as tg_filters, get_ids, admin_command, help

HANDLERS = [
    handlers.MessageHandler(
        get_ids.get_forward,
        filters.private
        & filters.forwarded
        & (
                filters.all & ~filters.media_group
                | filters.create(tg_filters.is_media_group_exists)
        )
        & ~ filters.create(tg_filters.status_answer())
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.MessageHandler(
        get_ids.choose_lang,
        filters.private
        & tg_filters.start_command(command="lang")
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.MessageHandler(
        get_ids.get_me,
        filters.private
        & tg_filters.start_command(command="me")
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.MessageHandler(
        get_ids.get_chats_manager,
        filters.private
        & tg_filters.start_command(command="admin")
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.MessageHandler(
        get_ids.welcome,
        filters.private
        & tg_filters.start_command(command="start")
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.MessageHandler(
        get_ids.added_to_group,
        filters.private
        & tg_filters.start_command(command="add")
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.MessageHandler(
        get_ids.get_ids_in_the_group,
        filters.group
        & tg_filters.start_command(command="id")
    ),
    handlers.MessageHandler(
        help.handle_callback_data_help,
        filters.private
        & tg_filters.start_command(command="help")
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.MessageHandler(
        get_ids.send_about,
        filters.private
        & tg_filters.start_command(command="about")
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.MessageHandler(
        get_ids.get_username,
        filters.private
        & filters.create(tg_filters.is_username)
        & ~ filters.create(tg_filters.status_answer())
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.MessageHandler(
        get_ids.get_contact,
        filters.private
        & filters.contact
        & ~ filters.create(tg_filters.status_answer(answer=True))
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.MessageHandler(
        get_ids.get_request_peer,
        filters.private
        & filters.create(lambda _, __, msg: msg.chat_shared is not None or msg.users_shared is not None)
        & ~ filters.create(tg_filters.status_answer())
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.MessageHandler(
        get_ids.get_story,
        filters.private
        & filters.create(lambda _, __, msg: msg.story is not None)
        & ~ filters.create(tg_filters.status_answer())
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    # admin command
    handlers.MessageHandler(
        admin_command.get_stats,
        filters.private
        & filters.command("stats")
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_admin)
    ),
    handlers.MessageHandler(
        admin_command.get_message_for_subscribe,
        filters.private
        & (
                tg_filters.start_command(command="send")
                & ~ filters.create(tg_filters.status_answer()) |
                filters.create(tg_filters.status_answer(send_message_to_subscribers=True))
        )
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_admin)
    ),

    handlers.ChatMemberUpdatedHandler(
        get_ids.on_remove_permission,
        # filters.admin
    ),

    # callback
    handlers.CallbackQueryHandler(
        help.handle_callback_data_help,
        filters.create(lambda _, __, cbd: cbd.data.startswith("help"))
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.CallbackQueryHandler(
        get_ids.get_lang,
        filters.create(lambda _, __, cbd: cbd.data.startswith("lang"))
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
    ),
    handlers.CallbackQueryHandler(
        admin_command.send_message_to_subscribers,
        filters.create(lambda _, __, cbd: cbd.data.startswith("send"))
        & filters.create(tg_filters.is_user_spamming)
        & filters.create(tg_filters.create_user)
        & filters.create(tg_filters.is_admin)
    ),

    handlers.RawUpdateHandler(get_ids.get_raw),
]
