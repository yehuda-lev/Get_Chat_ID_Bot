from pyrogram import Client, types, enums, raw, errors

from tg import filters
from tg.filters import check_username
from tg.strings import get_text
from db import filters as db_filters


async def welcome(_: Client, msg: types.Message):
    """start the bot"""
    tg_id = msg.from_user.id
    name = msg.from_user.first_name + (
        " " + last if (last := msg.from_user.last_name) else ""
    )

    await msg.reply_text(
        text=get_text(text="WELCOME", tg_id=tg_id).format(name=name),
        disable_web_page_preview=True,
        reply_markup=types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [
                    # user
                    types.KeyboardButton(
                        text=get_text("USER", tg_id),
                        request_peer=types.RequestUserInfo(
                            button_id=1, is_bot=False, max_quantity=10
                        ),
                    ),
                    # bot
                    types.KeyboardButton(
                        text=get_text("BOT", tg_id),
                        request_peer=types.RequestUserInfo(button_id=2, is_bot=True),
                    ),
                ],
                [
                    # group
                    types.KeyboardButton(
                        text=get_text("GROUP", tg_id),
                        request_peer=types.RequestChatInfo(button_id=3),
                    ),
                    # channel
                    types.KeyboardButton(
                        text=get_text("CHANNEL", tg_id),
                        request_peer=types.RequestChannelInfo(button_id=4),
                    ),
                ],
            ],
        ),
    )


async def get_chats_manager(_: Client, msg: types.Message):
    """Get chats manager"""
    tg_id = msg.from_user.id
    text = get_text(text="CHAT_MANAGER", tg_id=tg_id)

    await msg.reply_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [
                    # group
                    types.KeyboardButton(
                        text=get_text("GROUP", tg_id),
                        request_peer=types.RequestChatInfo(
                            button_id=3,
                            user_privileges=types.ChatPrivileges(can_manage_chat=True),
                        ),
                    ),
                    # channel
                    types.KeyboardButton(
                        text=get_text("CHANNEL", tg_id),
                        request_peer=types.RequestChannelInfo(
                            button_id=4,
                            user_privileges=types.ChatPrivileges(
                                can_manage_chat=True,
                            ),
                        ),
                    ),
                ],
            ],
        ),
    )


async def choice_lang(_, msg: types.Message):
    """Choice language"""
    tg_id = msg.from_user.id
    await msg.reply(
        text=get_text("CHOICE_LANG", tg_id=tg_id),
        reply_markup=types.InlineKeyboardMarkup(
            [
                [types.InlineKeyboardButton(text="עברית 🇮🇱", callback_data="he")],
                [types.InlineKeyboardButton(text="English 🇱🇷", callback_data="en")],
            ]
        ),
        reply_to_message_id=msg.id,
    )


async def get_lang(_, query: types.CallbackQuery):
    """Get language"""
    lang = query.data
    tg_id = query.from_user.id
    db_filters.change_lang(tg_id=tg_id, lang=lang)
    await query.answer(
        text=get_text(text="DONE", tg_id=tg_id).format(lang), show_alert=True
    )


async def get_forward(_, msg: types.Message):
    """Get message forward"""
    tg_id = msg.from_user.id
    if isinstance(msg.forward_from, types.User):
        # user
        text = get_text("ID_USER", tg_id).format(f"`{msg.forward_from.id}`")
    elif isinstance(msg.forward_from_chat, types.Chat):
        # channel
        text = get_text("ID_CHANNEL_OR_GROUP", tg_id).format(
            f"`{msg.forward_from_chat.id}`"
        )
    elif msg.forward_sender_name:
        # The user hides the forwarding of a message from him or Deleted Account
        text = get_text("ID_HIDDEN", tg_id).format(name=msg.forward_sender_name)
    else:
        return
    await msg.reply(text=text, reply_to_message_id=msg.id)


async def get_me(_, msg: types.Message):
    """Get id the user"""
    tg_id = msg.from_user.id
    await msg.reply(
        get_text("ID_USER", tg_id).format(f"`{msg.from_user.id}`"),
        reply_to_message_id=msg.id,
    )


async def get_contact(_, msg: types.Message):
    """Get id from contact"""
    tg_id = msg.from_user.id
    if msg.contact.user_id:
        text = get_text("ID_USER", tg_id).format(f"`{msg.contact.user_id}`")
    else:
        text = get_text("NOT_HAVE_ID", tg_id)
    await msg.reply(text=text, reply_to_message_id=msg.id)


async def get_request_peer(_: Client, msg: types.Message):
    """"Get request peer"""
    tg_id = msg.from_user.id

    request_chat = msg.requested_chats
    match request_chat[0].type:
        case enums.ChatType.PRIVATE:
            request_users = (
                f"`{request_chat[0].id}`"
                if len(request_chat) == 1
                else ("".join(f"\n`{user.id}`" for user in request_chat))
            )

            text = get_text("ID_USER", tg_id).format(request_users)
        case enums.ChatType.GROUP:
            text = get_text("ID_CHANNEL_OR_GROUP", tg_id).format(
                f"`{request_chat[0].id}`"
            )
        case enums.ChatType.CHANNEL:
            text = get_text("ID_CHANNEL_OR_GROUP", tg_id).format(
                f"`{request_chat[0].id}`"
            )
        case _:
            return

    await msg.reply(text=text, quote=True)


async def get_story(_: Client, msg: types.Message):
    """Get id from story"""
    tg_id = msg.from_user.id

    await msg.reply(
        text=get_text("ID_CHANNEL_OR_GROUP", tg_id).format(f"`{msg.story.chat.id}`"),
        quote=True,
    )


async def get_about(_: Client, msg: types.Message):
    """Get info about the bot"""
    tg_id = msg.from_user.id
    await msg.reply_web_page(
        text=get_text(text="INFO_ABOUT", tg_id=tg_id),
        reply_to_message_id=msg.id,
        url="https://github.com/yehuda-lev/Get_Chat_ID_Bot",
        invert_media=True,
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        text=get_text(text="BUTTON_DEV", tg_id=tg_id),
                        url=get_text(text="LINK_DEV", tg_id=tg_id)
                    )
                ],
            ]
        )

    )


async def get_username(client: Client, msg: types.Message):
    """Get id from username or link"""
    tg_id = msg.from_user.id

    username = check_username(text=msg.text)

    try:
        chat = await client.get_chat(username)
    except errors.BadRequest as e:
        await msg.reply_text(text=get_text("CAN_NOT_GET_THE_ID", tg_id), quote=True)
        return

    else:
        if isinstance(chat, types.Chat):
            match chat.type:
                case enums.ChatType.PRIVATE:
                    text = get_text("ID_USER", tg_id).format(f"`{chat.id}`")
                case enums.ChatType.BOT:
                    text = get_text("ID_USER", tg_id).format(f"`{chat.id}`")
                case enums.ChatType.GROUP:
                    text = get_text("ID_CHANNEL_OR_GROUP", tg_id).format(f"`{chat.id}`")
                case enums.ChatType.CHANNEL:
                    text = get_text("ID_CHANNEL_OR_GROUP", tg_id).format(f"`{chat.id}`")
                case enums.ChatType.SUPERGROUP:
                    text = get_text("ID_CHANNEL_OR_GROUP", tg_id).format(f"`{chat.id}`")
                case _:
                    return
        else:
            text = get_text("CAN_NOT_GET_THE_ID", tg_id)

        await msg.reply_text(text=text, quote=True)


async def get_raw(client: Client, update: raw.types.UpdateNewMessage, _, __):
    """get reply in another chat"""
    if isinstance(update, raw.types.UpdateNewMessage):
        if isinstance(update.message, raw.types.Message):
            tg_id = update.message.peer_id.user_id

            # check user spamming
            if not filters.is_spamming(tg_id=tg_id):
                return

            if update.message.reply_to:
                if isinstance(update.message.reply_to, raw.types.MessageReplyHeader):
                    if reply_to := update.message.reply_to:
                        # reply in another chat
                        reply_to_chat_id, reply_from_id, reply_from_name = (
                            None,
                            None,
                            None,
                        )

                        if reply_to.reply_to_peer_id:
                            match type(reply_to.reply_to_peer_id):
                                case raw.types.PeerChannel:
                                    reply_to_chat_id = get_text(
                                        "ID_CHANNEL_OR_GROUP", tg_id
                                    ).format(
                                        f"`-100{reply_to.reply_to_peer_id.channel_id}`"
                                    )
                                case raw.types.PeerUser:
                                    reply_to_chat_id = get_text(
                                        "ID_USER", tg_id
                                    ).format(f"`{reply_to.reply_to_peer_id.user_id}`")
                                case raw.types.PeerChat:
                                    reply_to_chat_id = get_text(
                                        "ID_USER", tg_id
                                    ).format(f"`{reply_to.reply_to_peer_id.chat_id}`")
                                case _:
                                    return

                        if reply_to.reply_from.from_id:
                            match type(reply_to.reply_from.from_id):
                                case raw.types.PeerChannel:
                                    reply_from_id = get_text(
                                        "ID_CHANNEL_OR_GROUP", tg_id
                                    ).format(
                                        f"`-100{reply_to.reply_from.from_id.channel_id}`"
                                    )

                                case raw.types.PeerUser:
                                    reply_from_id = get_text("ID_USER", tg_id).format(
                                        f"`{reply_to.reply_from.from_id.user_id}`"
                                    )

                                case raw.types.PeerChat:
                                    reply_from_id = get_text("ID_USER", tg_id).format(
                                        f"`{reply_to.reply_from.from_id.chat_id}`"
                                    )
                                case _:
                                    return

                        else:
                            reply_from_name = get_text("ID_HIDDEN", tg_id).format(
                                name=reply_to.reply_from.from_name
                            )

                        if reply_from_id:
                            text = reply_from_id
                        elif reply_from_name:
                            text = reply_from_name
                        elif reply_to_chat_id:
                            text = reply_to_chat_id
                        else:
                            return

                        await client.send_message(
                            chat_id=tg_id,
                            text=text,
                            reply_to_message_id=update.message.id,
                        )
