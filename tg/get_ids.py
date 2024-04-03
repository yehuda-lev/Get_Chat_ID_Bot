from pyrogram import Client, types, enums, raw, errors

from tg import filters
from tg.filters import check_username
from tg.strings import get_text
from db import repository


async def welcome(_: Client, msg: types.Message):
    """start the bot"""
    tg_id = msg.from_user.id
    name = msg.from_user.first_name + (
        " " + last if (last := msg.from_user.last_name) else ""
    )

    await msg.reply_text(
        text=get_text(text="WELCOME", tg_id=tg_id).format(name=name),
        link_preview_options=types.LinkPreviewOptions(is_disabled=True),
        reply_markup=types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            input_field_placeholder=get_text("CHOSE_CHAT_TYPE", tg_id=tg_id),
            keyboard=[
                [
                    # user
                    types.KeyboardButton(
                        text=get_text("USER", tg_id),
                        request_users=types.KeyboardButtonRequestUsers(
                            request_id=1, user_is_bot=False, max_quantity=10, request_name=True
                        ),
                    ),
                    # bot
                    types.KeyboardButton(
                        text=get_text("BOT", tg_id),
                        request_users=types.KeyboardButtonRequestUsers(
                            request_id=2, user_is_bot=True, max_quantity=10, request_name=True
                        ),
                    ),
                ],
                [
                    # group
                    types.KeyboardButton(
                        text=get_text("GROUP", tg_id),
                        request_chat=types.KeyboardButtonRequestChat(
                            request_id=3, chat_is_channel=False, request_title=True,
                        ),
                    ),
                    # channel
                    types.KeyboardButton(
                        text=get_text("CHANNEL", tg_id),
                        request_chat=types.KeyboardButtonRequestChat(
                            request_id=4, chat_is_channel=True, request_title=True,
                        ),
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
        link_preview_options=types.LinkPreviewOptions(is_disabled=True),
        reply_markup=types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            input_field_placeholder=get_text("CHOSE_CHAT_TYPE", tg_id=tg_id),
            keyboard=[
                [
                    # group
                    types.KeyboardButton(
                        text=get_text("GROUP", tg_id),
                        request_chat=types.KeyboardButtonRequestChat(
                            request_id=3, chat_is_channel=False, request_title=True,
                            user_administrator_rights=types.ChatPrivileges(can_manage_chat=True)
                        ),
                    ),
                    # channel
                    types.KeyboardButton(
                        text=get_text("CHANNEL", tg_id),
                        request_chat=types.KeyboardButtonRequestChat(
                            request_id=4, chat_is_channel=True, request_title=True,
                            user_administrator_rights=types.ChatPrivileges(can_manage_chat=True)
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
        quote=True,
    )


async def get_lang(_, query: types.CallbackQuery):
    """Get language"""
    lang = query.data
    tg_id = query.from_user.id
    repository.change_lang(tg_id=tg_id, lang=lang)
    await query.edit_message_text(
        text=get_text(text="DONE", tg_id=tg_id).format(lang),
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
    await msg.reply(text=text, quote=True)


async def get_me(_, msg: types.Message):
    """Get id the user"""
    tg_id = msg.from_user.id
    await msg.reply(
        text=get_text("ID_USER", tg_id).format(f"`{msg.from_user.id}`"),
        quote=True,
    )


async def get_contact(_, msg: types.Message):
    """Get id from contact"""
    tg_id = msg.from_user.id
    if msg.contact.user_id:
        text = get_text("ID_USER", tg_id).format(f"`{msg.contact.user_id}`")
    else:
        text = get_text("NOT_HAVE_ID", tg_id)
    await msg.reply(text=text, quote=True)


async def get_request_peer(_: Client, msg: types.Message):
    """"Get request peer"""
    tg_id = msg.from_user.id

    # TODO added name of chats
    reply_markup = None

    if msg.users_shared:
        users = msg.users_shared.users
        request_users = (
            f"`{users[0].id}`"
            if len(users) == 1
            else ("".join(f"\n`{user.id}`" for user in users))
        )

        text = get_text("ID_USER", tg_id).format(request_users)
    elif msg.chat_shared:
        request_chat = msg.chat_shared
        if request_chat.request_id == 100:
            text = get_text("BOT_ADDED_TO_GROUP", tg_id).format(
                group_id=f"`{request_chat.chats[0].id}`"
            )
            reply_markup = types.ReplyKeyboardRemove()

        else:
            text = get_text("ID_CHANNEL_OR_GROUP", tg_id).format(
                f"`{msg.chat_shared.chats[0].id}`"
            )
    else:
        return

    await msg.reply(text=text, quote=True, reply_markup=reply_markup)


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
    await msg.reply_text(
        text=get_text(text="INFO_ABOUT", tg_id=tg_id),
        quote=True,
        link_preview_options=types.LinkPreviewOptions(
            url="https://github.com/yehuda-lev/Get_Chat_ID_Bot",
            show_above_text=True,
        ),
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
    except errors.BadRequest:
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


async def added_to_group(_: Client, msg: types.Message):
    """
    Added the bot to the group
    """
    tg_id = msg.from_user.id
    await msg.reply(
        text=get_text("ADD_BOT_TO_GROUP", tg_id),
        quote=True,
        reply_markup=types.ReplyKeyboardMarkup(
            [
                [
                    types.KeyboardButton(
                        text=get_text("BUTTON_ADD_BOT_TO_GROUP", tg_id),
                        request_chat=types.KeyboardButtonRequestChat(
                            request_id=100, chat_is_channel=False, request_title=True,
                            user_administrator_rights=types.ChatPrivileges(
                                can_manage_chat=True, can_promote_members=True
                            ),
                            bot_administrator_rights=types.ChatPrivileges(can_manage_chat=True)
                        ),
                    )
                ]
            ],
            resize_keyboard=True
        )
    )


async def on_remove_permission(client: Client, msg: types.ChatMemberUpdated):
    """
    on remove permission,
    if remove permission. the bot will leave the group
    """
    if msg.new_chat_member:
        if msg.new_chat_member.status == enums.ChatMemberStatus.RESTRICTED:
            await client.leave_chat(chat_id=msg.chat.id)


async def get_ids_in_the_group(client: Client, msg: types.Message):
    """
    get ids in the group
    """
    chat_id, name = None, None

    if filters.is_mention_users(msg):  # get is mention users
        for entity in msg.entities:
            if entity.type == enums.MessageEntityType.MENTION:
                try:
                    username = msg.text[entity.offset:entity.offset + entity.length]
                    user = await client.get_chat(username)
                    name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
                except errors.BadRequest:
                    break
                else:
                    break
            elif entity.type == enums.MessageEntityType.TEXT_MENTION:
                chat_id = entity.user.id
                name = f"{entity.user.first_name} {entity.user.last_name}" \
                    if entity.user.last_name else entity.user.first_name
                break
            else:
                continue

    else:  # get reply to chat id
        if msg.reply_to_story:
            chat = msg.reply_to_story.chat
            chat_id = chat.id
            name = chat.title if chat.title \
                else f"{chat.first_name} {chat.last_name}" if chat.last_name else chat.first_name
        elif msg.reply_to_message:
            if msg.reply_to_message.from_user:
                chat = msg.reply_to_message.from_user
                chat_id = chat.id
                name = f"{chat.first_name} {chat.last_name}" if chat.last_name else chat.first_name
            elif msg.reply_to_message.sender_chat:
                chat = msg.reply_to_message.sender_chat
                chat_id = chat.id
                name = chat.title
            else:
                return
        else:
            chat_id = msg.chat.id
            name = msg.chat.title

    if not chat_id or not name:
        return

    try:
        await msg.reply(text=f"{name} | `{chat_id}`", quote=True)
    except Exception:  # noqa
        await client.leave_chat(chat_id=msg.chat.id)


async def get_reply_to_another_chat(client: Client, update: raw.types.UpdateNewMessage):
    """
    get reply to another chat
    """
    reply_to = update.message.reply_to
    tg_id = update.message.peer_id.user_id

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

    if reply_to.reply_from:
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
        message_thread_id=update.message.id,
    )


async def get_raw(client: Client, update: raw.types.UpdateNewMessage, _, __):
    """
    Handle raw message
    """
    if isinstance(update, raw.types.UpdateNewMessage):
        if isinstance(update.message, raw.types.Message):
            if not update.message.peer_id and not update.message.peer_id.user_id:
                return
            tg_id = update.message.peer_id.user_id

            # check user spamming
            if not filters.is_spamming(tg_id=tg_id):
                return

            if update.message.reply_to:
                if isinstance(update.message.reply_to, raw.types.MessageReplyHeader):
                    # reply to another chat
                    await get_reply_to_another_chat(client, update)
