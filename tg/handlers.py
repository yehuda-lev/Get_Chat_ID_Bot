import logging
from pyrogram import handlers, filters

from tg import (
    filters as tg_filters,
    get_ids,
    admin_command,
    help,
    payments,
    code_runner,
    stats,
)

_logger = logging.getLogger(__name__)

HANDLERS = [
    handlers.MessageHandler(
        get_ids.get_forward,
        filters.private
        & ~filters.tg_business
        & filters.forwarded
        & (
            filters.all & ~filters.media_group
            | filters.create(tg_filters.is_media_group_exists)
        )
        & ~tg_filters.status_answer()
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    # commands
    handlers.MessageHandler(
        get_ids.choose_lang,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command(command="lang")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.get_me,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command(command="me")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.get_chats_manager,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command(command="admin")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.added_to_group,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command(command="add")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.get_ids_in_the_group,
        filters.group
        & ~filters.tg_business  # not needed, but maybe in the future
        & filters.command("id")
        & tg_filters.create_group(),
    ),
    handlers.MessageHandler(
        help.handle_callback_data_help,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command(command="help")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.send_about,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command(command="about")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        payments.ask_for_payment,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command(command="donate")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.send_privacy_policy,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command("privacy")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.send_link_to_chat_by_id,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command("link")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.ask_inline_query,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command("search")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    # other
    handlers.MessageHandler(
        get_ids.get_username_by_message,
        filters.private
        & ~filters.tg_business
        & filters.text
        & filters.create(tg_filters.is_username)
        & ~tg_filters.status_answer()
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.get_contact,
        filters.private
        & ~filters.tg_business
        & filters.contact
        & ~tg_filters.status_answer()
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.get_request_peer,
        filters.private
        & ~filters.tg_business
        & filters.create(
            lambda _, __, msg: msg.chat_shared is not None
            or msg.users_shared is not None
        )
        & ~tg_filters.status_answer()
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.get_story,
        filters.private
        & ~filters.tg_business
        & filters.create(lambda _, __, msg: msg.story is not None)
        & ~tg_filters.status_answer()
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.get_via_bot,
        filters.private
        & ~filters.tg_business
        & filters.create(
            lambda _, client, msg: msg.via_bot and client.me.id != msg.via_bot.id
        ),
    ),
    handlers.MessageHandler(
        get_ids.get_reply_to_another_chat,
        filters.private
        & ~filters.tg_business
        & filters.create(lambda _, __, msg: msg.external_reply is not None)
        & ~tg_filters.status_answer()
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.ChatMemberUpdatedHandler(
        get_ids.on_remove_permission,
    ),
    # business
    handlers.MessageHandler(
        get_ids.get_id_with_business_connection,
        filters.tg_business
        & tg_filters.start_command(command="id", prefixes=[".", "/"])
        & filters.outgoing
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.MessageHandler(
        get_ids.get_id_by_manage_business,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command(command="bizChat")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.BusinessBotConnectionHandler(
        get_ids.handle_business_connection,
        tg_filters.create_user(),
    ),
    # welcome
    handlers.MessageHandler(
        get_ids.welcome,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command(command="start")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    # callback
    handlers.CallbackQueryHandler(
        help.handle_callback_data_help,
        filters.create(lambda _, __, cbd: cbd.data.startswith("help"))
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.CallbackQueryHandler(
        get_ids.get_lang,
        filters.create(lambda _, __, cbd: cbd.data.startswith("lang"))
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    # inline query
    handlers.InlineQueryHandler(
        get_ids.get_username_by_inline_query,
        filters.create(tg_filters.is_username)
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    # payments
    handlers.CallbackQueryHandler(
        payments.send_payment,
        filters.create(lambda _, __, cbd: cbd.data.startswith("stars"))
        & tg_filters.is_user_spamming()
        & tg_filters.create_user(),
    ),
    handlers.PreCheckoutQueryHandler(
        payments.confirm_payment,
        ~filters.tg_business,
    ),
    handlers.MessageHandler(
        payments.send_thanks_for_support,
        filters.successful_payment & tg_filters.create_user(),
    ),
    # admin command
    handlers.MessageHandler(
        code_runner.python_exec,
        filters=(
            ~filters.me
            & ~filters.tg_business
            & filters.private
            & filters.command(["py", "rpy"], prefixes="/")
            & tg_filters.is_admin()
            & ~filters.forwarded
        ),
    ),
    # stats
    handlers.MessageHandler(
        stats.ask_stats_time,
        filters.private
        & ~filters.tg_business
        & filters.command("stats")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user()
        & tg_filters.is_admin(),
    ),
    handlers.CallbackQueryHandler(
        stats.ask_stats_language,
        filters.create(lambda _, __, msg: msg.data.startswith("ask_stats"))
        & tg_filters.is_user_spamming()
        & tg_filters.create_user()
        & tg_filters.is_admin(),
    ),
    handlers.CallbackQueryHandler(
        stats.get_stats,
        filters.create(lambda _, __, msg: msg.data.startswith("get_stats"))
        & tg_filters.is_user_spamming()
        & tg_filters.create_user()
        & tg_filters.is_admin(),
    ),
    # broadcast
    handlers.MessageHandler(
        admin_command.ask_for_who_to_send,
        filters.private
        & ~filters.tg_business
        & tg_filters.start_command("send")
        & tg_filters.is_user_spamming()
        & tg_filters.create_user()
        & tg_filters.is_admin(),
    ),
    handlers.MessageHandler(
        admin_command.delete_sent_messages,
        filters.command("delete")
        & ~filters.tg_business
        & tg_filters.create_user()
        & tg_filters.is_admin(),
    ),
    handlers.CallbackQueryHandler(
        admin_command.asq_message_for_subscribe,
        filters.create(lambda _, __, msg: msg.data.startswith("send"))
        & tg_filters.is_user_spamming()
        & tg_filters.create_user()
        & tg_filters.is_admin(),
    ),
    handlers.MessageHandler(
        admin_command.send_broadcast,
        filters.private
        & ~filters.tg_business
        & tg_filters.status_answer({"send_message_to_subscribers": True})
        & tg_filters.is_user_spamming()
        & tg_filters.create_user()
        & tg_filters.is_admin(),
    ),
]
