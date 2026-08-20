import io
import asyncio
import logging
import random
import string
import time
from pathlib import Path

from pyrogram import Client, types, errors

from db import repository
from tg import filters
from tg.broadcast import (
    BroadcastStateError,
    broadcast_recipients,
    build_broadcast_log_file,
    get_broadcast_scope,
)


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
    state = filters.user_id_to_state.get(tg_id)
    try:
        send_to = get_broadcast_scope(state)
    except BroadcastStateError:
        _logger.warning("Broadcast requested without an active state for %s", tg_id)
        await msg.reply("לא נמצא מצב שליחה פעיל. נסה להתחיל מחדש עם `/send`")
        return
    finally:
        filters.remove_listener_by_tg_id(tg_id=tg_id)

    recipients: list[object]
    recipient_kind: str
    if send_to == "users":
        recipients = await repository.get_all_users_active()
        recipient_kind = "user"
    else:
        recipients = await repository.get_all_groups_active()
        recipient_kind = "group"

    log_obj = io.StringIO()

    while True:
        sent_id = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        if not await repository.is_message_sent_exists(sent_id=sent_id):
            break

    await msg.reply(
        text=(
            f"**📣 מתחיל שליחה ל:** {len(recipients)} צ'אטים\nאנא המתן...\n"
            f"> מזהה השליחה: `{sent_id}` ניתן להשתמש בו בכדי למחוק את ההודעות שנשלחו עם הפקודה `/delete {sent_id}`"
        ),
    )
    progress = await msg.reply(text="**ההודעה נשלחת ל:** 0 צ'אטים")

    async def deliver(recipient: object) -> bool:
        recipient_chat_id = recipient.tg_id if recipient_kind == "user" else recipient.group_id
        try:
            if msg.forward_origin:
                msg_sent = await msg.forward(chat_id=recipient_chat_id)
            else:
                msg_sent = await msg.copy(chat_id=recipient_chat_id)

            await repository.create_message_sent(
                sent_id=sent_id,
                chat_id=recipient_chat_id,
                message_id=msg_sent.id,
            )

            if recipient_kind == "user":
                text_log = (
                    f"sent to user: {recipient.tg_id}, name: {recipient.name}, "
                    f"language_code: {recipient.language_code}, username: {recipient.username}\n"
                )
            else:
                text_log = (
                    f"sent to group: {recipient.group_id}, name: {recipient.name}, "
                    f"username: {recipient.username}\n"
                )

            log_obj.write(text_log)
            _logger.debug(text_log)
            return True

        except errors.FloodWait as e:
            _logger.error("FloodWait while broadcasting to %s: %s", recipient_chat_id, e.value)
            await progress.edit_text(
                text=f"**ההודעה מושהית בגלל FloodWait:** {e.value} שניות",
            )
            await asyncio.sleep(e.value)
            return False

        except errors.InputUserDeactivated:
            if recipient_kind == "user":
                await repository.update_user(tg_id=recipient.tg_id, active=False)
                text_log = (
                    f"user {recipient.tg_id}, name: {recipient.name} "
                    f"language_code: {recipient.language_code}, username: {recipient.username} is Deactivated\n"
                )
            else:
                await repository.update_group(group_id=recipient.group_id, active=False)
                text_log = (
                    f"group {recipient.group_id}, name: {recipient.name}, username: {recipient.username} is Deactivated\n"
                )
            log_obj.write(text_log)
            _logger.debug(text_log)
            return False

        except errors.UserIsBlocked:
            if recipient_kind == "user":
                await repository.update_user(tg_id=recipient.tg_id, active=False)
                text_log = (
                    f"user {recipient.tg_id}, name: {recipient.name} "
                    f"language_code: {recipient.language_code}, username: {recipient.username} Blocked your bot\n"
                )
            else:
                await repository.update_group(group_id=recipient.group_id, active=False)
                text_log = (
                    f"group {recipient.group_id}, name: {recipient.name}, username: {recipient.username} Blocked your bot\n"
                )
            log_obj.write(text_log)
            _logger.debug(text_log)
            return False

        except errors.PeerIdInvalid:
            if recipient_kind == "user":
                await repository.update_user(tg_id=recipient.tg_id, active=False)
                text_log = (
                    f"user {recipient.tg_id}, name: {recipient.name} "
                    f"language_code: {recipient.language_code}, username: {recipient.username} IdInvalid\n"
                )
            else:
                await repository.update_group(group_id=recipient.group_id, active=False)
                text_log = (
                    f"group {recipient.group_id}, name: {recipient.name}, username: {recipient.username} IdInvalid\n"
                )
            log_obj.write(text_log)
            _logger.debug(text_log)
            return False

        except errors.BadRequest as e:
            if recipient_kind == "user":
                await repository.update_user(tg_id=recipient.tg_id, active=False)
                text_log = (
                    f"BadRequest: {e} : user {recipient.tg_id}, name: {recipient.name} "
                    f"language_code: {recipient.language_code}, username: {recipient.username}\n"
                )
            else:
                await repository.update_group(group_id=recipient.group_id, active=False)
                text_log = (
                    f"BadRequest: {e} : group {recipient.group_id}, name: {recipient.name}, username: {recipient.username}\n"
                )
            log_obj.write(text_log)
            _logger.debug(text_log)
            return False

    async def update_progress(recipient: object, sent_count: int):
        if sent_count % 10 == 0:
            await progress.edit_text(
                text=f"**ההודעה נשלחה ל:** {sent_count} צ'אטים",
            )

    sent, failed = await broadcast_recipients(
        recipients,
        deliver,
        on_success=update_progress,
    )

    text_log = f"\n\nSent: {sent}, Failed: {failed}\n Sent_id: {sent_id}\n\n"
    log_obj.write(text_log)
    _logger.debug(text_log)

    log_file_path = build_broadcast_log_file(log_obj.getvalue())
    text_done = (
        f"📣 השליחה הושלמה\n\n🔹ההודעה נשלחה ל: {sent} צ'אטים\n"
        f"🔹 ההודעה נכשלה ב: {failed} צ'אטים"
        f"\n\n🔹 מזהה השליחה: {sent_id}\n"
        f"🔹 נשלח בתאריך: {time.strftime('%d/%m/%Y')}\n"
        f"🔹 נשלח בשעה: {time.strftime('%H:%M:%S')}\n"
        f"\nניתן למחוק את ההודעות על ידי שליחת הפקודה `/delete {sent_id}`"
    )

    try:
        await msg.reply_document(document=log_file_path, caption=text_done)
    except Exception as e:
        _logger.exception(e)
        await msg.reply(f"```py\n{e}```")
    finally:
        Path(log_file_path).unlink(missing_ok=True)


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
