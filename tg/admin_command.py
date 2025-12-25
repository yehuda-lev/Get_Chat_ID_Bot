import io
import logging
import random
import string
import tempfile
import time
from pyrogram import Client, types, errors

from db import repository
from tg import filters


_logger = logging.getLogger(__name__)


async def ask_for_who_to_send(_: Client, msg: types.Message):
    await msg.reply(
        text="למי ברצונך לשלוח הודעה?",
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        text="לכל המשתמשים", callback_data="send:users"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="לכל הקבוצות",
                        callback_data="send:groups",
                    )
                ],
                [types.InlineKeyboardButton(text="ביטול", callback_data="send:no")],
            ]
        ),
    )


async def asq_message_for_subscribe(_: Client, msg: types.CallbackQuery):
    match send_to := msg.data.split(":")[-1]:
        case "users":
            send_to = send_to
            text = "כל המשתמשים"
        case "groups":
            send_to = send_to
            text = "כל הקבוצות"
        case "no":
            await msg.answer("ההודעה לא תישלח")
            await msg.message.edit_text("בוטל")
            return
        case _:
            return

    await msg.message.reply(
        text=f"אנא שלח את ההודעה שתרצה לשלוח ל{text}\n "
        f"> אם ההודעה תועבר עם קרדיט, הבוט גם יעביר את ההודעה עם קרדיט",
    )
    filters.add_listener(
        tg_id=msg.from_user.id,
        data={"send_message_to_subscribers": True, "data": send_to},
    )


async def send_broadcast(_: Client, msg: types.Message):
    tg_id = msg.from_user.id
    send_to: str = filters.user_id_to_state.get(tg_id).get("data")

    filters.user_id_to_state.pop(tg_id)

    # users, chats = None, None
    match send_to:
        case "users":
            users = await repository.get_all_users_active()
            chats = None
        case "groups":
            chats = await repository.get_all_groups_active()
            users = None
        case _:
            return

    log_obj = io.StringIO()

    sent = 0
    failed = 0
    count = 0
    count_edit = 0

    while True:
        sent_id = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        if not await repository.is_message_sent_exists(sent_id=sent_id):
            break

    await msg.reply(
        text=f"**📣 מתחיל שליחה ל:** {len((chats if chats is not None else users))} צ'אטים\nאנא המתן...\n"
        f"> מזהה השליחה: `{sent_id}` ניתן להשתמש בו בכדי למחוק את ההודעות שנשלחו עם הפקודה `/delete {sent_id}`",
    )
    progress = await msg.reply(text=f"**ההודעה נשלחת ל:** {sent} צ'אטים")

    if users is not None:  # send to users
        for user in users:
            if count > 40:
                count = 0
                time.sleep(3)
            try:
                if msg.forward_origin:
                    msg_sent = await msg.forward(chat_id=user.tg_id)
                else:
                    msg_sent = await msg.copy(chat_id=user.tg_id)
                sent += 1

                await repository.create_message_sent(
                    sent_id=sent_id, chat_id=user.tg_id, message_id=msg_sent.id
                )

                if count_edit + 10 == sent:
                    count_edit += 10
                    await progress.edit_text(
                        text=f"**ההודעה נשלחה ל:** {sent} צ'אטים",
                    )

                text_log = (
                    f"sent to user: {user.tg_id}, name: {user.name}, "
                    f"language_code: {user.language_code}, username: {user.username}\n"
                )
                log_obj.write(text_log)
                _logger.debug(text_log)
                count += 1
                time.sleep(
                    0.05
                )  # 20 messages per second (Limit: 30 messages per second)

            except errors.FloodWait as e:
                _logger.error(f"FloodWait: {e.value}")
                time.sleep(e.value)

            except errors.InputUserDeactivated:
                await repository.update_user(tg_id=user.tg_id, active=False)
                text_log = (
                    f"user {user.tg_id}, name: {user.name} "
                    f"language_code: {user.language_code}, username: {user.username} is Deactivated\n"
                )
                log_obj.write(text_log)
                _logger.debug(text_log)
                failed += 1
                continue

            except errors.UserIsBlocked:
                await repository.update_user(tg_id=user.tg_id, active=False)
                text_log = f"user {user.tg_id}, name: {user.name} language_code: {user.language_code}, username: {user.username} Blocked your bot\n"
                log_obj.write(text_log)
                _logger.debug(text_log)
                failed += 1
                continue

            except errors.PeerIdInvalid:
                await repository.update_user(tg_id=user.tg_id, active=False)
                text_log = f"user {user.tg_id}, name: {user.name} language_code: {user.language_code}, username: {user.username} IdInvalid\n"
                log_obj.write(text_log)
                _logger.debug(text_log)
                failed += 1
                continue

            except errors.BadRequest as e:
                await repository.update_user(tg_id=user.tg_id, active=False)
                text_log = f"BadRequest: {e} : user {user.tg_id}, name: {user.name} language_code: {user.language_code}, username: {user.username}"
                log_obj.write(text_log)
                _logger.debug(text_log)
                failed += 1
                continue

    if chats is not None:  # send to chats
        for chat in chats:
            if count > 40:
                count = 0
                time.sleep(3)
            try:
                if msg.forward_origin:
                    msg_sent = await msg.forward(chat_id=chat.group_id)
                else:
                    msg_sent = await msg.copy(chat_id=chat.group_id)
                sent += 1

                await repository.create_message_sent(
                    sent_id=sent_id, chat_id=chat.group_id, message_id=msg_sent.id
                )

                if count_edit + 10 == sent:
                    count_edit += 10
                    await progress.edit_text(
                        text=f"**ההודעה נשלחה ל:** {sent} צ'אטים",
                    )

                text_log = f"sent to user: {chat.group_id}, name: {chat.name} username: {chat.username}\n"
                log_obj.write(text_log)
                _logger.debug(text_log)
                count += 1
                time.sleep(
                    0.05
                )  # 20 messages per second (Limit: 30 messages per second)

            except errors.FloodWait as e:
                _logger.error(f"FloodWait: {e.value}")
                time.sleep(e.value)

            except errors.BadRequest as e:
                await repository.update_group(group_id=chat.group_id, active=False)
                text_log = f"BadRequest: {e}, chat_id: {chat.group_id}, name: {chat.name}, username: {chat.username}"
                log_obj.write(text_log)
                _logger.debug(text_log)
                failed += 1
                continue

    text_done = (
        f"📣 השליחה הושלמה\n\n🔹ההודעה נשלחה ל: {sent} צ'אטים\n"
        f"🔹 ההודעה נכשלה ב: {failed} צ'אטים"
        f"\n\n🔹 מזהה השליחה: {sent_id}\n"
        f"🔹 נשלח בתאריך: {time.strftime('%d/%m/%Y')}\n"
        f"🔹 נשלח בשעה: {time.strftime('%H:%M:%S')}\n"
        f"\nניתן למחוק את ההודעות על ידי שליחת הפקודה `/delete {sent_id}`"
    )

    text_log = f"\n\nSent: {sent}, Failed: {failed}\n Sent_id: {sent_id}\n\n"
    log_obj.write(text_log)
    _logger.debug(text_log)

    with tempfile.TemporaryFile(delete=False) as temp_file:
        # write log to file
        temp_file.write(log_obj.getvalue().encode())
        temp_file.flush()
        temp_file_path = temp_file.name

        try:
            await msg.reply_document(document=temp_file_path, caption=text_done)
        except Exception as e:
            _logger.exception(e)
            await msg.reply(f"```py\n{e}```")


async def delete_sent_messages(client: Client, msg: types.Message):
    """
    Delete sent messages.
    when the user sends the command /delete
    """
    try:
        sent_id = msg.text.split(" ")[1]
    except IndexError:
        await msg.reply("לא נמצא מזהה של ההודעות שנשלחו")
        return

    if not await repository.is_message_sent_exists(sent_id=sent_id):
        await msg.reply("המזהה אינו תקין")
        return

    sent_messages = await repository.get_messages_sent(sent_id=sent_id)
    await msg.reply(f"מוחק {len(sent_messages)} הודעות שנשלחו")

    count = 0
    delete = 0
    for sent_message in sent_messages:
        if count > 40:
            count = 0
            time.sleep(3)

        try:
            await client.delete_messages(
                chat_id=sent_message.chat_id, message_ids=sent_message.message_id
            )
            count += 1
            time.sleep(0.05)  # 20 messages per second (Limit: 30 messages per second)
            delete += 1

        except errors.FloodWait as e:
            _logger.error(f"FloodWait: {e.value}")
            time.sleep(e.value)

        except Exception as e:
            _logger.error(
                f"Error: {e}, chat_id: {sent_message.chat_id}, message_id: {sent_message.message_id}"
            )

    await msg.reply(f"נמחקו {delete} הודעות")
