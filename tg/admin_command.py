import os
import time

from pyrogram import Client, types
from pyrogram.errors import PeerIdInvalid, FloodWait, UserIsBlocked, BadRequest, InputUserDeactivated

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

        log_file = open('logger.txt', 'a+')
        users = db_filters.get_users_active()
        sent = 0
        failed = 0

        c.send_message(chat_id=tg_id, text=f"**📣 starting broadcast to:** "
                                           f"`{len(users)} users`\nPlease Wait...")
        progress = c.send_message(chat_id=tg_id, text=f'**Message Sent To:** `{sent} users`')

        for chat in users:
            # print(chat)
            # sleep_count(count)
            try:
                c.copy_message(chat_id=int(chat), from_chat_id=tg_id,
                               message_id=reply_msg_id)
                sent += 1

                c.edit_message_text(chat_id=tg_id, message_id=progress.id,
                                    text=f'**Message Sent To:** `{sent}` users')

                log_file.write(f"sent to {chat} \n")
                # count += 1
                time.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)

            except FloodWait as e:
                print(e)
                time.sleep(e.value)

            except InputUserDeactivated:
                db_filters.change_active(tg_id=chat, active=False)
                log_file.write(f"user {chat} is Deactivated\n")
                failed += 1
                continue

            except UserIsBlocked:
                db_filters.change_active(tg_id=chat, active=False)
                log_file.write(f"user {chat} Blocked your bot\n")
                failed += 1
                continue

            except PeerIdInvalid:
                db_filters.change_active(tg_id=chat, active=False)
                log_file.write(f"user {chat} IdInvalid\n")
                failed += 1
                continue

            except BadRequest as e:
                db_filters.change_active(tg_id=chat, active=False)
                log_file.write(f"BadRequest: {e} :{chat}")
                failed += 1
                continue

        c.delete_messages(chat_id=tg_id, message_ids=msg_id)

        text_done = f"📣 Broadcast Completed\n\n🔸 **Total Users in db:** " \
                    f"{len(users)}\n\n🔹 Message sent to: {sent} users\n" \
                    f"🔹 Failed to sent: {failed} users"

        log_file.write('\n\n' + text_done + '\n')

        c.send_message(chat_id=tg_id, text=text_done)

        log_file.close()
        try:
            c.send_document(chat_id=tg_id, document='logger.txt')
        except Exception as e:
            c.send_message(chat_id=tg_id, text=str(e))
        finally:
            os.remove('logger.txt')


def sleep_count(count):  # delete?
    if count > 20:
        count = 0
        time.sleep(5)
    return count
