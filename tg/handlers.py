from pyrogram import Client, filters, types, client, handlers
from pyrogram.raw.types import (KeyboardButtonRequestPeer, RequestPeerTypeUser, ReplyKeyboardMarkup,
                                KeyboardButtonRow, UpdateNewMessage, RequestPeerTypeChat, RequestPeerTypeBroadcast)
from pyrogram.raw.functions.messages import SendMessage

from tg import filters as tg_filters


async def start(c: Client, msg: types.Message):
    name = msg.from_user.first_name + \
           (" " + last if (last := msg.from_user.last_name) else "")
    text2 = "בבוט זה תוכל לקבל id של קבוצה ערוץ או משתמש"
    text = f"ברוך הבא {name}\n\n{text2}\n\n" \
           f"בשביל להשתמש בבוט אנא לחצו על הכפתורים למטה ושתפו את הערוץ הקבוצה או המשתמש."
    peer = await c.resolve_peer(msg.chat.id)
    await c.invoke(
        SendMessage(peer=peer, message=text, random_id=c.rnd_id(),
                    reply_markup=ReplyKeyboardMarkup(rows=[
                        KeyboardButtonRow(
                            buttons=[
                                KeyboardButtonRequestPeer(text='משתמש',
                                                          button_id=1,
                                                          peer_type=RequestPeerTypeUser()),
                                KeyboardButtonRequestPeer(text='קבוצה',
                                                          button_id=2,
                                                          peer_type=RequestPeerTypeChat()),
                                KeyboardButtonRequestPeer(text='ערוץ',
                                                          button_id=3,
                                                          peer_type=RequestPeerTypeBroadcast())
                            ]
                        )

                    ], resize=True))
    )


async def raw(c: Client, update: UpdateNewMessage, users, chats):
    try:
        if update.message.action.button_id:
            button_id = update.message.action.button_id
            chat = update.message.action.peer
            if button_id == 1:
                print("user")
                text = f"ה ID הוא: `{chat.user_id}`"
            elif button_id == 2:
                print("group")
                text = f"ה ID הוא: `-100{chat.channel_id}`"
            else:
                print("channel")
                text = f"ה ID הוא: `-100{chat.channel_id}`"
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
    handlers.RawUpdateHandler(raw)
]
