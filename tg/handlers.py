from pyrogram import Client, filters, types, handlers
from pyrogram.raw.types import (KeyboardButtonRequestPeer, RequestPeerTypeUser, ReplyKeyboardMarkup,
                                KeyboardButtonRow, UpdateNewMessage, RequestPeerTypeChat,
                                RequestPeerTypeBroadcast, PeerChat, PeerChannel, MessageService,
                                MessageActionRequestedPeer, PeerUser, Message, MessageMediaStory)
from pyrogram.raw.functions.messages import SendMessage
from pyrogram.types import User, Chat, InlineKeyboardMarkup, InlineKeyboardButton

from tg import filters as tg_filters
from tg.admin_command import get_stats, send_message, get_message_for_subscribe
from tg.strings import get_text
from db import filters as db_filters


async def start(c: Client, msg: types.Message):
    tg_id = msg.from_user.id
    name = msg.from_user.first_name + (
        " " + last if (last := msg.from_user.last_name) else "")
    text = get_text(text='WELCOME', tg_id=tg_id).format(name=name)
    peer = await c.resolve_peer(msg.chat.id)
    await c.invoke(
        SendMessage(peer=peer, message=text, random_id=c.rnd_id(), no_webpage=True,
                    reply_markup=ReplyKeyboardMarkup(rows=[
                        KeyboardButtonRow(
                            buttons=[
                                KeyboardButtonRequestPeer(text=get_text('USER', tg_id),
                                                          button_id=1,
                                                          peer_type=RequestPeerTypeUser(bot=False)),
                                KeyboardButtonRequestPeer(text=get_text('BOT', tg_id),
                                                          button_id=2,
                                                          peer_type=RequestPeerTypeUser(bot=True))]),
                        KeyboardButtonRow(
                            buttons=[

                                KeyboardButtonRequestPeer(text=get_text('GROUP', tg_id),
                                                          button_id=3,
                                                          peer_type=RequestPeerTypeChat()),
                                KeyboardButtonRequestPeer(text=get_text('CHANNEL', tg_id),
                                                          button_id=4,
                                                          peer_type=RequestPeerTypeBroadcast())
                            ]
                        )

                    ], resize=True))
    )


def choice_lang(_, msg: types.Message):
    tg_id = msg.from_user.id
    msg.reply(
        text=get_text('CHOICE_LANG', tg_id=tg_id),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='עברית 🇮🇱', callback_data='he')],
            [InlineKeyboardButton(text='English 🇱🇷', callback_data='en')]
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
    if isinstance(msg.forward_from, User):
        # user
        text = get_text('ID_USER', tg_id).format(f'`{msg.forward_from.id}`')
    elif isinstance(msg.forward_from_chat, Chat):
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


async def raw_message(c: Client, update: UpdateNewMessage, _, __):
    if isinstance(update, UpdateNewMessage):
        if update.message:
            match update.message:
                case MessageService():
                    if update.message.action:
                        if isinstance(update.message.action, MessageActionRequestedPeer):
                            tg_id = update.message.peer_id.user_id
                            chat = update.message.action.peer

                            match chat:
                                case PeerUser():
                                    # user or bot
                                    text = get_text('ID_USER', tg_id).format(f'`{chat.user_id}`')
                                case PeerChat():
                                    # group
                                    text = get_text('ID_USER', tg_id).format(f'`{chat.chat_id}`')
                                case PeerChannel():
                                    # channel or super group
                                    text = get_text('ID_CHANNEL_OR_GROUP', tg_id).format(f'`-100{chat.channel_id}`')
                                case _:
                                    return
                        else:
                            return
                        await c.send_message(chat_id=update.message.peer_id.user_id,
                                             reply_to_message_id=update.message.id, text=text)
                case Message():
                    if update.message.media:
                        if isinstance(update.message.media, MessageMediaStory):
                            tg_id = update.message.peer_id.user_id
                            story = update.message.media
                            text = get_text('ID_USER', tg_id).format(f'`{story.user_id}`')
                        else:
                            return
                        await c.send_message(chat_id=update.message.peer_id.user_id,
                                             reply_to_message_id=update.message.id, text=text)
                case _:
                    return


HANDLERS = [
    handlers.MessageHandler(start, filters.text & filters.command("start")
                            & filters.private & filters.create(tg_filters.create_user)),
    handlers.MessageHandler(choice_lang, filters.text & filters.command("lang")
                            & filters.private & filters.create(tg_filters.create_user)),
    handlers.MessageHandler(get_me, filters.text & filters.command("me")
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
    handlers.CallbackQueryHandler(send_message, filters.create(tg_filters.create_user)
                                  & filters.create(tg_filters.is_admin)),
    handlers.RawUpdateHandler(raw_message)
]
