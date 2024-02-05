import os
import time

from pyrogram import Client, types
from pyrogram.errors import (
    PeerIdInvalid,
    FloodWait,
    UserIsBlocked,
    BadRequest,
    InputUserDeactivated,
)

from db import repository
from tg import filters as tg_filters


async def get_stats(_: Client, msg: types.Message):
    text = (
        f"כמות המשתמשים בבוט היא: {repository.get_tg_count()} "
        f"\nכמות המנויים הפעילים היא: {repository.get_tg_active_count()}"
    )
    await msg.reply(text)


# in the admin want to send message for everyone
async def get_message_for_subscribe(_, msg: types.Message):
    tg_id = msg.from_user.id
    if not tg_filters.status_answer(tg_id=tg_id):
        await msg.reply(
            text="אנא שלח את המידע אותו תרצה להעביר למנויים",
        )
        tg_filters.add_listener(tg_id=tg_id, data={"send_message_to_subscribers": True})

    # ask if want to send this message to subscribers
    else:
        await msg.reply(
            reply_to_message_id=msg.id,
            text="לשלוח את ההודעה?",
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(text="כן", callback_data="send:yes"),
                        types.InlineKeyboardButton(text="לא", callback_data="send:no"),
                    ]
                ]
            ),
        )


async def send_message_to_subscribers(client: Client, query: types.CallbackQuery):
    tg_id = query.from_user.id

    tg_filters.remove_listener_by_wa_id(tg_id=tg_id)

    msg_id = query.message.id
    if query.data == "send:no":
        await client.send_message(chat_id=tg_id, text="ההודעה לא תישלח למנויים")
        await client.delete_messages(chat_id=tg_id, message_ids=msg_id)

    # send message to subscribers
    else:
        reply_msg_id = query.message.reply_to_message.id
        message_to_send = await client.get_messages(
            chat_id=tg_id, message_ids=reply_msg_id
        )

        name_file = f"logger_{query.id}.txt"
        log_file = open(name_file, "a+", encoding="utf-8")

        users = repository.get_users_active()
        sent = 0
        failed = 0
        count = 0
        count_edit = 0

        await client.send_message(
            chat_id=tg_id,
            text=f"**📣 starting broadcast to:** "
            f"`{len(users)} users`\nPlease Wait...",
        )
        progress = await client.send_message(
            chat_id=tg_id, text=f"**Message Sent To:** `{sent} users`"
        )

        for chat in users:
            user = repository.get_user_by_tg_id(tg_id=int(chat))

            # print(chat)
            if count > 40:
                count = 0
                time.sleep(3)
            try:
                if message_to_send.forward_date:
                    await message_to_send.forward(
                        chat_id=int(user.tg_id),
                    )
                else:
                    await message_to_send.copy(
                        chat_id=int(user.tg_id),
                    )
                sent += 1

                if count_edit + 10 == sent:
                    count_edit += 10
                    await client.edit_message_text(
                        chat_id=tg_id,
                        message_id=progress.id,
                        text=f"**Message Sent To:** `{sent}` users",
                    )

                log_file.write(f"sent to user: {user.tg_id}, name: {user.name} lang: {user.lang} \n")
                count += 1
                time.sleep(
                    0.05
                )  # 20 messages per second (Limit: 30 messages per second)

            except FloodWait as e:
                print(e)
                time.sleep(e.value)

            except InputUserDeactivated:
                repository.change_active(tg_id=int(user.tg_id), active=False)
                log_file.write(f"user {user.tg_id}, name: {user.name} lang: {user.lang} is Deactivated\n")
                failed += 1
                continue

            except UserIsBlocked:
                repository.change_active(tg_id=int(user.tg_id), active=False)
                log_file.write(f"user {user.tg_id}, name: {user.name} lang: {user.lang} Blocked your bot\n")
                failed += 1
                continue

            except PeerIdInvalid:
                repository.change_active(tg_id=int(user.tg_id), active=False)
                log_file.write(f"user {user.tg_id}, name: {user.name} lang: {user.lang} IdInvalid\n")
                failed += 1
                continue

            except BadRequest as e:
                repository.change_active(tg_id=int(user.tg_id), active=False)
                log_file.write(f"BadRequest: {e} : user {user.tg_id}, name: {user.name} lang: {user.lang}")
                failed += 1
                continue

        await client.delete_messages(chat_id=tg_id, message_ids=msg_id)

        text_done = (
            f"📣 Broadcast Completed\n\n🔸 **Total Users in db:** "
            f"{len(users)}\n\n🔹 Message sent to: {sent} users\n"
            f"🔹 Failed to sent: {failed} users"
        )

        log_file.write("\n\n" + text_done + "\n")

        await client.send_message(chat_id=tg_id, text=text_done)

        log_file.close()
        try:
            await client.send_document(chat_id=tg_id, document=name_file)
        except Exception as e:
            await client.send_message(chat_id=tg_id, text=str(e))
        finally:
            os.remove(name_file)
