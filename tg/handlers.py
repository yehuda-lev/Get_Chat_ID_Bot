from pyrogram import Client, filters, types, handlers
from pyrogram.raw.types import (KeyboardButtonRequestPeer, RequestPeerTypeUser, ReplyKeyboardMarkup,
                                KeyboardButtonRow, UpdateNewMessage, RequestPeerTypeChat,
                                RequestPeerTypeBroadcast, PeerChat, PeerChannel)
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
    text2 = get_text('INFO1', tg_id)
    text3 = get_text('INFO2', tg_id)
    text4 = get_text('INFO3', tg_id)
    text = get_text(text='WELCOME', tg_id=tg_id).format(name=name, start2=text2,
                                                        start3=text3, start4=text4)
    peer = await c.resolve_peer(msg.chat.id)
    await c.invoke(
        SendMessage(peer=peer, message=text, random_id=c.rnd_id(),
                    reply_markup=ReplyKeyboardMarkup(rows=[
                        KeyboardButtonRow(
                            buttons=[
                                KeyboardButtonRequestPeer(text=get_text('USER', tg_id),
                                                          button_id=1,
                                                          peer_type=RequestPeerTypeUser()),
                                KeyboardButtonRequestPeer(text=get_text('GROUP', tg_id),
                                                          button_id=2,
                                                          peer_type=RequestPeerTypeChat()),
                                KeyboardButtonRequestPeer(text=get_text('CHANNEL', tg_id),
                                                          button_id=3,
                                                          peer_type=RequestPeerTypeBroadcast())
                            ]
                        )

                    ], resize=True))
    )


def choice_lang(_, msg: types.Message):
    tg_id = msg.from_user.id
    msg.reply(text=get_text('CHOICE_LANG', tg_id=tg_id),
              reply_markup=InlineKeyboardMarkup([
                  [InlineKeyboardButton(text='עברית 🇮🇱', callback_data='he')],
                  [InlineKeyboardButton(text='English 🇱🇷', callback_data='en')]
              ]))


def get_lang(_, query: types.CallbackQuery):
    lang = query.data
    tg_id = query.from_user.id
    db_filters.change_lang(tg_id, lang=lang)
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
        text = get_text('', tg_id).format(name=msg.forward_sender_name)
    else:
        return
    msg.reply(text=text)


async def raw(c: Client, update: UpdateNewMessage, users, chats):
    try:
        if update.message.action.button_id:
            tg_id = update.message.peer_id.user_id
            button_id = update.message.action.button_id
            chat = update.message.action.peer
            if button_id == 1:
                # print("user")
                text = get_text('ID_USER', tg_id).format(f'`{chat.user_id}`')
            elif button_id == 2:
                if isinstance(chat, PeerChat):
                    # print('group')
                    text = get_text('ID_USER', tg_id).format(f'`{chat.chat_id}`')
                elif isinstance(chat, PeerChannel):
                    # print('super group')
                    text = get_text('ID_CHANNEL_OR_GROUP', tg_id).format(f'`-100{chat.channel_id}`')
                else:
                    return
            else:
                # print("channel")
                text = get_text('ID_CHANNEL_OR_GROUP', tg_id).format(f'`-100{chat.channel_id}`')
        else:
            return
        await c.send_message(chat_id=update.message.peer_id.user_id,
                             reply_to_message_id=update.message.id, text=text)
        return
    except AttributeError:
        return


HANDLERS = [
    handlers.MessageHandler(start, filters.text & filters.command("start")
                            & filters.private & filters.create(tg_filters.create_user)),
    handlers.MessageHandler(choice_lang, filters.text & filters.command("lang")
                            & filters.private & filters.create(tg_filters.create_user)),
    handlers.MessageHandler(forward, filters.forwarded & filters.private
                            & filters.create(tg_filters.create_user)),
    handlers.MessageHandler(get_stats, filters.text & filters.command("stats")
                            & filters.private & filters.create(tg_filters.create_user)
                            & filters.create(tg_filters.is_admin)),
    handlers.MessageHandler(get_message_for_subscribe, filters.private &
                            (filters.text & filters.command("send") | filters.reply &
                             ~ filters.command(["send", "stats", "start"])
                             & filters.create(tg_filters.is_force_reply))
                            & filters.create(tg_filters.create_user)
                            & filters.create(tg_filters.is_admin)
                            & filters.create(tg_filters.is_not_raw)),
    handlers.CallbackQueryHandler(get_lang, filters.create(tg_filters.create_user)
                                  & filters.create(tg_filters.query_lang)),
    handlers.CallbackQueryHandler(send_message, filters.create(tg_filters.create_user)
                                  & filters.create(tg_filters.is_admin)),
    handlers.RawUpdateHandler(raw)
]
