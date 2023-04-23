import time

from pyrogram import Client, types
from pyrogram.errors import PeerIdInvalid, FloodWait, UserIsBlocked, BadRequest

from db import filters as db_filters


def get_stats(c: Client, msg: types.Message):
    text = f'כמות המשתמשים בבוט היא: {db_filters.get_tg_count()} ' \
           f'\nכמות המנויים הפעילים היא: {db_filters.get_tg_active_count()}'
    msg.reply(text)


# in the admin want to send message for everyone
def get_message_for_subscribe(_, msg: types.Message):
    if msg.command:
        if msg.command[0] == 'send':
            msg.reply(text='אנא שלח את המידע אותו תרצה להעביר למנויים',
                      reply_markup=types.ForceReply(selective=True,
                                                    placeholder='אנא שלח את המידע..'))
    elif isinstance(msg.reply_to_message.reply_markup, types.ForceReply):
        msg.reply(reply_to_message_id=msg.id, text='לשלוח את ההודעה?',
                  reply_markup=types.InlineKeyboardMarkup(
                      [[
                          types.InlineKeyboardButton(text="כן", callback_data='yes'),
                          types.InlineKeyboardButton(text="לא", callback_data='no')
                      ]]))


def send_message(c: Client, query: types.CallbackQuery):
    tg_id = query.from_user.id
    msg_id = query.message.id
    reply_msg_id = query.message.reply_to_message.id
    if query.data == 'no':
        c.send_message(chat_id=tg_id, text='ההודעה לא תישלח למנויים')
        c.delete_messages(chat_id=tg_id, message_ids=msg_id)
    elif query.data == 'yes':
        count = 0
        for chat in db_filters.get_users_active():
            print(chat)
            sleep_count(count)
            try:
                c.copy_message(chat_id=int(chat), from_chat_id=tg_id,
                               message_id=reply_msg_id)
                count += 1
            except FloodWait as e:
                print(e)
                time.sleep(e.value)
            except (UserIsBlocked, BadRequest, PeerIdInvalid):
                db_filters.change_active(tg_id=chat, active=False)
        c.delete_messages(chat_id=tg_id, message_ids=msg_id)
        c.send_message(chat_id=tg_id, text='ההודעה נשלחה למנויים')


def sleep_count(count):
    if count > 20:
        count = 0
        time.sleep(5)
    return count
