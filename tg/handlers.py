from pyrogram import Client, filters, types, handlers, enums, raw

from tg import filters as tg_filters
from tg.admin_command import get_stats, send_message, get_message_for_subscribe
from tg.strings import get_text
from db import filters as db_filters


async def welcome(_: Client, msg: types.Message):
    tg_id = msg.from_user.id
    name = msg.from_user.first_name + (
        " " + last if (last := msg.from_user.last_name) else "")

    await msg.reply_text(
        text=get_text(text='WELCOME', tg_id=tg_id).format(name=name),
        disable_web_page_preview=True,
        reply_markup=types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [
                    # user
                    types.KeyboardButton(
                        text=get_text('USER', tg_id),
                        request_peer=types.RequestUserInfo(button_id=1, is_bot=False)),
                    # bot
                    types.KeyboardButton(
                        text=get_text('BOT', tg_id),
                        request_peer=types.RequestUserInfo(button_id=2, is_bot=True))
                ],
                [
                    # group
                    types.KeyboardButton(
                        text=get_text('GROUP', tg_id),
                        request_peer=types.RequestChatInfo(button_id=3)),
                    # channel
                    types.KeyboardButton(
                        text=get_text('CHANNEL', tg_id),
                        request_peer=types.RequestChannelInfo(button_id=4))
                ],
            ],
        )
    )


async def get_chats_manager(c: Client, msg: types.Message):
    tg_id = msg.from_user.id
    text = get_text(text='CHAT_MANAGER', tg_id=tg_id)
    peer = await c.resolve_peer(msg.chat.id)
    await c.invoke(
        raw.functions.messages.SendMessage(
            peer=peer, message=text, random_id=c.rnd_id(), no_webpage=True,
            reply_markup=raw.types.ReplyKeyboardMarkup(rows=[
                raw.types.KeyboardButtonRow(
                    buttons=[
                        raw.types.KeyboardButtonRequestPeer(
                            text=get_text('GROUP', tg_id),
                            button_id=1,
                            peer_type=raw.types.RequestPeerTypeChat(
                                user_admin_rights=raw.types.ChatAdminRights(other=True)
                            )),
                        raw.types.KeyboardButtonRequestPeer(
                            text=get_text('CHANNEL', tg_id),
                            button_id=2,
                            peer_type=raw.types.RequestPeerTypeBroadcast(
                                user_admin_rights=raw.types.ChatAdminRights(other=True)
                            )),
                    ]
                )
            ], resize=True))
    )


def choice_lang(_, msg: types.Message):
    tg_id = msg.from_user.id
    msg.reply(
        text=get_text('CHOICE_LANG', tg_id=tg_id),
        reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton(text='עברית 🇮🇱', callback_data='he')],
            [types.InlineKeyboardButton(text='English 🇱🇷', callback_data='en')],
        ]),
        reply_to_message_id=msg.id
    )


def get_lang(_, query: types.CallbackQuery):
    lang = query.data
    tg_id = query.from_user.id
    db_filters.change_lang(tg_id=tg_id, lang=lang)
    query.answer(text=get_text(text='DONE', tg_id=tg_id).format(lang), show_alert=True)


def forward(_, msg: types.Message):
    tg_id = msg.from_user.id
    if isinstance(msg.forward_from, types.User):
        # user
        text = get_text('ID_USER', tg_id).format(f'`{msg.forward_from.id}`')
    elif isinstance(msg.forward_from_chat, types.Chat):
        # channel
        text = get_text('ID_CHANNEL_OR_GROUP', tg_id).format(f'`{msg.forward_from_chat.id}`')
    elif msg.forward_sender_name:
        # The user hides the forwarding of a message from him or Deleted Account
        text = get_text('ID_HIDDEN', tg_id).format(name=msg.forward_sender_name)
    else:
        return
    msg.reply(text=text, reply_to_message_id=msg.id)


def get_me(_, msg: types.Message):
    """Get id the user"""
    tg_id = msg.from_user.id
    msg.reply(get_text('ID_USER', tg_id).format(f'`{msg.from_user.id}`'), reply_to_message_id=msg.id)


def get_contact(_, msg: types.Message):
    tg_id = msg.from_user.id
    if msg.contact.user_id:
        text = get_text('ID_USER', tg_id).format(f'`{msg.contact.user_id}`')
    else:
        text = get_text('NOT_HAVE_ID', tg_id)
    msg.reply(text=text, reply_to_message_id=msg.id)


async def get_request_peer(_: Client, msg: types.Message):
    tg_id = msg.from_user.id

    request_chat = msg.requested_chat
    match request_chat.type:
        case enums.ChatType.PRIVATE:
            text = get_text('ID_USER', tg_id).format(f'`{request_chat.id}`')
        case enums.ChatType.GROUP:
            text = get_text('ID_CHANNEL_OR_GROUP', tg_id).format(f'`{request_chat.id}`')
        case enums.ChatType.CHANNEL:
            text = get_text('ID_CHANNEL_OR_GROUP', tg_id).format(f'`{request_chat.id}`')
        case _:
            return

    await msg.reply(
        text=text,
        quote=True
    )


async def get_story(_: Client, msg: types.Message):
    tg_id = msg.from_user.id

    await msg.reply(
        text=get_text('ID_CHANNEL_OR_GROUP', tg_id).format(f'`{msg.story.chat.id}`'),
        quote=True
    )


async def get_reply_to_another_chat(_: Client, msg: types.Message):
    tg_id = msg.from_user.id

    await msg.reply(
        text=get_text('ID_CHANNEL_OR_GROUP', tg_id).format(f'`{msg.reply_to_message.sender_chat.id}`'),
        quote=True
    )


def regex_start(arg: str):
    return filters.regex(rf"^/start ({arg})")


HANDLERS = [
    handlers.MessageHandler(choice_lang, filters.text & (filters.command("lang") | regex_start(arg='lang'))
                            & filters.private & filters.create(tg_filters.create_user)),
    handlers.MessageHandler(get_me, filters.text & (filters.command("me") | regex_start(arg='me'))
                            & filters.private & filters.create(tg_filters.create_user)),
    handlers.MessageHandler(get_chats_manager, filters.text & (filters.command("admin") | regex_start(arg='admin'))
                            & filters.private & filters.create(tg_filters.create_user)),
    handlers.MessageHandler(welcome, filters.text & filters.command("start")
                            & filters.private & filters.create(tg_filters.create_user)),
    handlers.MessageHandler(forward, filters.forwarded & filters.private
                            & filters.create(tg_filters.create_user)),
    handlers.MessageHandler(get_contact, filters.contact & filters.private
                            & filters.create(tg_filters.create_user)),
    handlers.MessageHandler(get_stats, filters.text & filters.command("stats")
                            & filters.private & filters.create(tg_filters.create_user)
                            & filters.create(tg_filters.is_admin)),
    handlers.MessageHandler(get_message_for_subscribe, filters.private &
                            (filters.text & filters.command("send") | filters.reply
                             & filters.create(tg_filters.is_force_reply))
                            & filters.create(tg_filters.create_user)
                            & filters.create(tg_filters.is_admin)
                            & filters.create(tg_filters.is_not_raw)),
    handlers.CallbackQueryHandler(get_lang, filters.create(tg_filters.create_user)
                                  & filters.create(tg_filters.query_lang)),
    handlers.CallbackQueryHandler(send_message, filters.create(lambda _, __, cbd: cbd.data.startswith('send')) &
                                  filters.create(tg_filters.create_user)
                                  & filters.create(tg_filters.is_admin)),
    handlers.MessageHandler(get_request_peer, filters=(
            filters.private
            & filters.create(lambda _, __, msg: msg.requested_chat is not None)  # filter requested_chat
            & filters.create(tg_filters.create_user)
        )
    ),
    handlers.MessageHandler(get_story, filters=(
            filters.private
            & filters.create(lambda _, __, msg: msg.story is not None)  # filter story
            & filters.create(tg_filters.create_user)
        )
    ),
    handlers.MessageHandler(get_reply_to_another_chat, filters=(
            filters.private
            & filters.reply
            #  filter reply to another chat
            & filters.create(lambda _, __, msg: msg.reply_to_message.sender_chat is not None)
            & filters.create(tg_filters.create_user)
        )
    ),
]
