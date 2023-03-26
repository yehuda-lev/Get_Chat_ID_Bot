from pyrogram import Client, filters, types
from pyrogram.raw.types import (KeyboardButtonRequestPeer, RequestPeerTypeUser, ReplyKeyboardMarkup,
                                KeyboardButtonRow, UpdateNewMessage, RequestPeerTypeChat, RequestPeerTypeBroadcast)
from pyrogram.raw.functions.messages import SendMessage


app = Client("my_bot", api_id="", api_hash="", bot_token="")


@app.on_message(filters.text | filters.command("start") & filters.private)
async def start(_, msg: types.Message):
    name = msg.from_user.first_name + (" " + last if (last := msg.from_user.last_name) else "")
    text2 = "בבוט זה תוכל לקבל id של קבוצה ערוץ או משתמש"
    text = f"ברוך הבא {name}\n\n{text2}\n\n"\
           f"בשביל להשתמש בבוט אנא לחצו על הכפתורים למטה ושתפו את הערוץ הקבוצה או המשתמש."
    try:
        peer = await app.resolve_peer(msg.chat.id)
        await app.invoke(
            SendMessage(peer=peer, message=text, random_id=app.rnd_id(),
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
    except Exception as e:
        print(e)


@app.on_raw_update()
async def raw(client, update: UpdateNewMessage, users, chats):
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
        await app.send_message(chat_id=update.message.peer_id.user_id,
                               reply_to_message_id=update.message.id, text=text)
        return
    except AttributeError:
        return
    except Exception as e:
        print(e)


app.run()
