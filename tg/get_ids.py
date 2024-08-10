import logging
from pyrogram import Client, types, enums, errors, raw, ContinuePropagation

from tg import filters, strings
from db import repository


_logger = logging.getLogger(__name__)


async def get_reply_markup(client: Client) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton(
                    text="Powered by 'Get Chat ID Bot' 🪪",
                    url=f"https://t.me/{client.me.username}?start=start",
                )
            ]
        ]
    )


async def welcome(_: Client, msg: types.Message):
    """start the bot"""
    user = msg.from_user
    tg_id = user.id
    name = user.full_name if user.full_name else ""
    lang = repository.get_user_language(tg_id=tg_id)

    await msg.reply_text(
        text=strings.get_text(key="WELCOME", lang=lang).format(name=name),
        link_preview_options=types.LinkPreviewOptions(is_disabled=True),
        message_effect_id=5107584321108051014,  # 👍
        reply_markup=types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            input_field_placeholder=strings.get_text(key="CHOSE_CHAT_TYPE", lang=lang),
            keyboard=[
                [
                    # user
                    types.KeyboardButton(
                        text=strings.get_text(key="USER", lang=lang),
                        request_users=types.KeyboardButtonRequestUsers(
                            request_id=1,
                            user_is_bot=False,
                            max_quantity=1,  # https://t.me/tgbetachat/1939059 not works
                            request_name=True,
                        ),
                    ),
                    # bot
                    types.KeyboardButton(
                        text=strings.get_text(key="BOT", lang=lang),
                        request_users=types.KeyboardButtonRequestUsers(
                            request_id=2,
                            user_is_bot=True,
                            max_quantity=1,
                            request_name=True,
                        ),
                    ),
                ],
                [
                    # group
                    types.KeyboardButton(
                        text=strings.get_text(key="GROUP", lang=lang),
                        request_chat=types.KeyboardButtonRequestChat(
                            request_id=3,
                            chat_is_channel=False,
                            request_title=True,
                        ),
                    ),
                    # channel
                    types.KeyboardButton(
                        text=strings.get_text(key="CHANNEL", lang=lang),
                        request_chat=types.KeyboardButtonRequestChat(
                            request_id=4,
                            chat_is_channel=True,
                            request_title=True,
                        ),
                    ),
                ],
            ],
        ),
    )


async def get_chats_manager(_: Client, msg: types.Message):
    """Get chats manager"""
    tg_id = msg.from_user.id
    lang = repository.get_user_language(tg_id=tg_id)
    text = strings.get_text(key="CHAT_MANAGER", lang=lang)

    await msg.reply_text(
        text=text,
        link_preview_options=types.LinkPreviewOptions(is_disabled=True),
        reply_markup=types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            input_field_placeholder=strings.get_text(key="CHOSE_CHAT_TYPE", lang=lang),
            keyboard=[
                [
                    # group
                    types.KeyboardButton(
                        text=strings.get_text(key="GROUP", lang=lang),
                        request_chat=types.KeyboardButtonRequestChat(
                            request_id=3,
                            chat_is_channel=False,
                            request_title=True,
                            user_administrator_rights=types.ChatPrivileges(
                                can_manage_chat=True
                            ),
                        ),
                    ),
                    # channel
                    types.KeyboardButton(
                        text=strings.get_text(key="CHANNEL", lang=lang),
                        request_chat=types.KeyboardButtonRequestChat(
                            request_id=4,
                            chat_is_channel=True,
                            request_title=True,
                            user_administrator_rights=types.ChatPrivileges(
                                can_manage_chat=True
                            ),
                        ),
                    ),
                ],
            ],
        ),
    )


async def choose_lang(_, msg: types.Message):
    """Choose language"""
    tg_id = msg.from_user.id
    lang = repository.get_user_language(tg_id=tg_id)

    await msg.reply(
        text=strings.get_text(key="CHOICE_LANG", lang=lang),
        reply_markup=types.InlineKeyboardMarkup(
            [
                [types.InlineKeyboardButton(text="עברית 🇮🇱", callback_data="lang:he")],
                [
                    types.InlineKeyboardButton(
                        text="English 🇱🇷", callback_data="lang:en"
                    )
                ],
            ]
        ),
        quote=True,
    )


async def get_lang(_, query: types.CallbackQuery):
    """Get language"""
    data_lang = query.data.split(":")[1]
    tg_id = query.from_user.id
    repository.update_user(tg_id=tg_id, language_code=data_lang)
    await query.edit_message_text(
        text=strings.get_text(key="DONE", lang=data_lang).format(data_lang),
    )


async def get_forward(_, msg: types.Message):
    """Get message forward"""
    tg_id = msg.from_user.id
    lang = repository.get_user_language(tg_id=tg_id)
    forward = msg.forward_origin
    # return

    if isinstance(forward, types.MessageOriginUser):  # user
        user = forward.sender_user
        text = strings.get_text(key="ID_USER", lang=lang).format(
            user.full_name if user.full_name else "",
            user.id,
        )
    elif isinstance(forward, types.MessageOriginChat):  # group
        group = forward.sender_chat
        text = strings.get_text(key="ID_CHANNEL_OR_GROUP", lang=lang).format(
            group.title, group.id
        )
    elif isinstance(forward, types.MessageOriginChannel):  # channel
        channel = forward.chat
        text = strings.get_text(key="ID_CHANNEL_OR_GROUP", lang=lang).format(
            channel.title, channel.id
        )
    elif isinstance(forward, types.MessageOriginHiddenUser):
        # The user hides the forwarding of a message from him or Deleted Account
        text = strings.get_text(key="ID_HIDDEN", lang=lang).format(
            name=forward.sender_user_name
        )
    else:
        return
    await msg.reply(text=text, quote=True)


async def get_me(_, msg: types.Message):
    """Get id the user"""
    user = msg.from_user
    tg_id = user.id
    lang = repository.get_user_language(tg_id=tg_id)

    await msg.reply(
        text=strings.get_text(key="ID_USER", lang=lang).format(
            user.full_name if user.full_name else "", tg_id
        ),
        quote=True,
    )


async def get_contact(_, msg: types.Message):
    """Get id from contact"""
    tg_id = msg.from_user.id
    lang = repository.get_user_language(tg_id=tg_id)

    if msg.contact.user_id:
        contact = msg.contact
        text = strings.get_text(key="ID_USER", lang=lang).format(
            contact.first_name
            + ((" " + contact.last_name) if contact.last_name else ""),
            contact.user_id,
        )
    else:
        text = strings.get_text(key="NOT_HAVE_ID", lang=lang)
    await msg.reply(text=text, quote=True)


async def get_request_peer(_: Client, msg: types.Message):
    """ "Get request peer"""
    tg_id = msg.from_user.id
    lang = repository.get_user_language(tg_id=tg_id)
    reply_markup = None

    if msg.users_shared:
        users = msg.users_shared.users
        if len(users) == 1:
            user = users[0]
            text = strings.get_text(key="ID_USER", lang=lang).format(
                user.full_name if user.full_name else "",
                user.id,
            )

        else:  # support of multiple users
            text = strings.get_text(key="ID_USERS", lang=lang).format(
                "".join(
                    f"\n`{user.id}` • {user.full_name if user.full_name else ''}"
                    for user in users
                )
            )
    elif msg.chat_shared:
        request_chat = msg.chat_shared
        chats = request_chat.chats

        if request_chat.request_id == 100:  # support of added to group
            chat = chats[0]

            if not repository.is_group_exists(group_id=chat.id):
                repository.create_group(
                    group_id=chat.id,
                    name=chat.title,
                    username=chat.username,
                    added_by_id=tg_id,
                )
            else:
                user = repository.get_user(tg_id=tg_id)
                repository.update_group(
                    group_id=chat.id, added_by_id=user.id, active=True
                )

            text = strings.get_text(key="BOT_ADDED_TO_GROUP", lang=lang).format(
                group_name=f"[{chat.title}](t.me/c/{str(chat.id).replace('-100', '')}/1000000000)",
                group_id=chat.id,
            )
            reply_markup = types.ReplyKeyboardRemove()

        else:
            if len(chats) == 1:
                chat = chats[0]
                text = strings.get_text(key="ID_CHANNEL_OR_GROUP", lang=lang).format(
                    chat.title, chat.id
                )
            else:  # support of multiple chats
                text = strings.get_text(key="ID_CHANNELS_OR_GROUPS", lang=lang).format(
                    "".join(f"\n{chat.title} • `{chat.id}`" for chat in chats)
                )
    else:
        return

    await msg.reply(text=text, quote=True, reply_markup=reply_markup)


async def get_story(_: Client, msg: types.Message):
    """Get id from story"""
    tg_id = msg.from_user.id
    lang = repository.get_user_language(tg_id=tg_id)
    chat = msg.story.chat

    match chat.type:
        case enums.ChatType.PRIVATE:  # user
            text = strings.get_text(key="ID_USER", lang=lang).format(
                chat.full_name if chat.full_name else "",
                chat.id,
            )
        case enums.ChatType.BOT:  # bot (when it's possible to upload story with bot)
            text = strings.get_text(key="ID_USER", lang=lang).format(
                chat.full_name if chat.full_name else "",
                chat.id,
            )
        case enums.ChatType.CHANNEL:  # channel
            text = strings.get_text(key="ID_CHANNEL_OR_GROUP", lang=lang).format(
                chat.title, chat.id
            )
        case enums.ChatType.SUPERGROUP:  # supergroup
            text = strings.get_text(key="ID_CHANNEL_OR_GROUP", lang=lang).format(
                chat.title, chat.id
            )
        case enums.ChatType.GROUP:  # group
            text = strings.get_text(key="ID_CHANNEL_OR_GROUP", lang=lang).format(
                chat.title, chat.id
            )
        case _:
            return

    await msg.reply(text=text, quote=True)


async def get_id_by_username(lang: str, client: Client, text: str) -> str:
    """Get id by username"""
    username = filters.get_username(text=text)

    try:
        chat = await client.get_chat(username)
    except errors.BadRequest:  # username not found
        text = strings.get_text(key="CAN_NOT_GET_THE_ID", lang=lang)

    else:
        if isinstance(chat, types.Chat):
            name = (
                chat.title if chat.title else chat.full_name if chat.full_name else ""
            )
            chat_id = chat.id
            if chat.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
                text = strings.get_text(key="ID_USER", lang=lang).format(name, chat_id)

            elif chat.type in (
                enums.ChatType.GROUP,
                enums.ChatType.SUPERGROUP,
                enums.ChatType.CHANNEL,
            ):
                text = strings.get_text(key="ID_CHANNEL_OR_GROUP", lang=lang).format(
                    name, chat_id
                )

        else:
            text = strings.get_text(key="CAN_NOT_GET_THE_ID", lang=lang)

    return text


async def get_username_by_message(client: Client, msg: types.Message):
    """Get id from username or link by message"""
    tg_id = msg.from_user.id
    lang = repository.get_user_language(tg_id=tg_id)

    text = await get_id_by_username(lang, client, msg.text)

    await msg.reply_text(text=text, quote=True)


async def get_username_by_inline_query(client: Client, query: types.InlineQuery):
    """
    Get id by inline query
    """

    lang = repository.get_user_language(tg_id=query.from_user.id)

    text = await get_id_by_username(lang, client, query.query)

    try:
        await query.answer(
            results=[
                types.InlineQueryResultArticle(
                    title="Get Chat ID",
                    id="1",
                    input_message_content=types.InputTextMessageContent(
                        message_text=text,
                    ),
                    reply_markup=await get_reply_markup(client),
                ),
            ],
            cache_time=5,
        )
    except errors.BadRequest as e:
        _logger.error(f"Can't answer to inline query {e}")


async def get_via_bot(_: Client, msg: types.Message):
    """Get id via bot"""

    tg_id = msg.via_bot.id
    name = msg.via_bot.first_name
    lang = repository.get_user_language(tg_id=tg_id)
    text = strings.get_text(key="ID_USER", lang=lang).format(name, tg_id)

    await msg.reply(text=text, quote=True)


async def added_to_group(_: Client, msg: types.Message):
    """
    Added the bot to the group
    """
    tg_id = msg.from_user.id
    lang = repository.get_user_language(tg_id=tg_id)

    await msg.reply(
        text=strings.get_text(key="ADD_BOT_TO_GROUP", lang=lang),
        quote=True,
        reply_markup=types.ReplyKeyboardMarkup(
            [
                [
                    types.KeyboardButton(
                        text=strings.get_text(key="BUTTON_ADD_BOT_TO_GROUP", lang=lang),
                        request_chat=types.KeyboardButtonRequestChat(
                            request_id=100,
                            chat_is_channel=False,
                            request_title=True,
                            request_username=True,
                            user_administrator_rights=types.ChatPrivileges(
                                can_manage_chat=True,
                                can_promote_members=True,
                                can_invite_users=True,
                            ),
                            bot_administrator_rights=types.ChatPrivileges(
                                can_manage_chat=True
                            ),
                        ),
                    )
                ]
            ],
            resize_keyboard=True,
        ),
    )


async def on_remove_permission(_: Client, update: types.ChatMemberUpdated):
    """
    When the bot has had permissions removed from a chat or user blocked the bot.
    """
    if not update.new_chat_member:
        return
    # user blocked the bot
    if update.from_user.id == update.chat.id:
        if (
            update.old_chat_member.status == enums.ChatMemberStatus.MEMBER
            and update.new_chat_member.status == enums.ChatMemberStatus.BANNED
        ):
            if repository.is_user_exists(tg_id=update.from_user.id):
                _logger.debug(
                    f"The bot has been stopped by the user: {update.from_user.id}, {update.from_user.first_name}"
                )
                repository.update_user(tg_id=update.from_user.id, active=False)

    # the bot has had permissions removed from a chat
    if not update.new_chat_member.user.is_self:
        return
    if update.new_chat_member.status in {
        enums.ChatMemberStatus.MEMBER,
        enums.ChatMemberStatus.RESTRICTED,
    } and (
        update.old_chat_member
        and update.old_chat_member.status is enums.ChatMemberStatus.ADMINISTRATOR
    ):
        _logger.debug(
            f"The bot has had permissions removed from: {update.chat.id}, {update.chat.title}"
        )
        repository.update_group(group_id=update.chat.id, active=False)


async def get_id_by_reply_to_another_chat(
    lang: str, msg: types.Message
) -> str | tuple[int, str]:
    """
    Get id by reply to another chat,
    if the message sent in a group than return the id and name of the group,
    else return the text of the message.
    """
    text, chat_id, name = None, None, None

    reply_to = msg.external_reply.origin

    if isinstance(reply_to, types.MessageOriginUser):  # user
        user = reply_to.sender_user
        name = user.full_name
        chat_id = user.id
        if lang:
            text = strings.get_text(key="ID_USER", lang=lang).format(
                name,
                chat_id,
            )
    elif isinstance(reply_to, types.MessageOriginChat):  # group
        group = reply_to.sender_chat
        name = group.title
        chat_id = group.id
        if lang:
            text = strings.get_text(key="ID_CHANNEL_OR_GROUP", lang=lang).format(
                name, chat_id
            )
    elif isinstance(reply_to, types.MessageOriginChannel):  # channel
        channel = reply_to.chat
        name = channel.title
        chat_id = channel.id
        if lang:
            text = strings.get_text(key="ID_CHANNEL_OR_GROUP", lang=lang).format(
                name, chat_id
            )
    elif isinstance(reply_to, types.MessageOriginHiddenUser):
        # The user hides the forwarding of a message from him or Deleted Account
        name = reply_to.sender_user_name
        if lang:
            text = strings.get_text(key="ID_HIDDEN", lang=lang).format(name=name)

    if lang:
        return text
    return chat_id, name


async def get_reply_to_message(lang, msg) -> str | tuple[int, str] | None:
    """
    Get reply to message
    """
    text, chat_id, name = None, None, None
    if msg.reply_to_message.from_user:
        chat = msg.reply_to_message.from_user
        chat_id = chat.id
        name = (
            chat.full_name
            if chat.full_name
            else ""
            if not chat.is_deleted
            else "Deleted Account"
        )
        if lang:
            text = strings.get_text(key="ID_USER", lang=lang).format(name, chat_id)
    elif msg.reply_to_message.sender_chat:
        chat = msg.reply_to_message.sender_chat
        chat_id = chat.id
        name = chat.title
        if lang:
            text = strings.get_text(key="ID_CHANNEL_OR_GROUP", lang=lang).format(
                name, chat_id
            )
    if lang:
        return text
    return chat_id, name


async def get_id_by_reply_to_story(lang, msg) -> str | tuple[int, str]:
    """
    Get id by reply to story
    """
    text, chat_id, name = None, None, None
    story = msg.reply_to_story
    if story.chat.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
        chat_id = story.chat.id
        name = story.chat.full_name if story.chat.full_name else ""
        if lang:
            text = strings.get_text(key="ID_USER", lang=lang).format(name, chat_id)
    elif story.chat.type in (
        enums.ChatType.CHANNEL,
        enums.ChatType.GROUP,
        enums.ChatType.SUPERGROUP,
    ):
        chat_id = story.chat.id
        name = story.chat.title
        if lang:
            text = strings.get_text(key="ID_CHANNEL_OR_GROUP", lang=lang).format(
                name, chat_id
            )
    if lang:
        return text
    return chat_id, name


async def get_id_by_reply(msg: types.Message) -> str | tuple[int, str]:
    """
    Get id by all reply types
    """
    lang = None

    if msg.chat.type == enums.ChatType.PRIVATE:
        tg_id = msg.from_user.id
        lang = repository.get_user_language(tg_id=tg_id)

    if msg.reply_to_story:
        return await get_id_by_reply_to_story(lang, msg)

    elif msg.reply_to_message:
        return await get_reply_to_message(lang, msg)

    # reply to another chat
    elif msg.external_reply:
        return await get_id_by_reply_to_another_chat(lang, msg)

    else:
        chat_id = msg.chat.id
        name = msg.chat.full_name or "" if lang else msg.chat.title
        if lang:
            return strings.get_text(key="ID_CHANNEL_OR_GROUP", lang=lang).format(
                name, chat_id
            )

    return chat_id, name


async def get_ids_in_the_group(client: Client, msg: types.Message):
    """
    get ids in the group
    """
    chat_id, name = None, None

    if filters.is_mention_users(msg):  # get is mention users
        for entity in msg.entities:
            if entity.type == enums.MessageEntityType.MENTION:
                try:
                    username = msg.text[entity.offset : entity.offset + entity.length]
                    user = await client.get_chat(username)
                    name = user.full_name if user.full_name else ""
                    chat_id = user.id
                except errors.BadRequest:
                    break
                else:
                    break
            elif entity.type == enums.MessageEntityType.TEXT_MENTION:
                chat_id = entity.user.id
                name = (
                    entity.full_name
                    if entity.full_name
                    else ""
                    if not entity.user.is_deleted
                    else "Deleted Account"
                )
                break
            else:
                continue

    else:  # get reply to chat id
        chat_id, name = await get_id_by_reply(msg)

    if not name:
        return

    try:
        await msg.reply(text=f"{name} • `{chat_id}`" if chat_id else name, quote=True)
    except Exception:  # noqa
        await client.leave_chat(chat_id=msg.chat.id)


async def get_reply_to_another_chat(_: Client, msg: types.Message):
    """
    get reply to another chat
    """
    tg_id = msg.from_user.id
    lang = repository.get_user_language(tg_id=tg_id)

    text = await get_id_by_reply_to_another_chat(lang, msg)

    if not text:
        return

    await msg.reply(text=text, quote=True)


async def get_id_with_business_connection(client: Client, msg: types.Message):
    """
    Get id with business connection.
    """

    text = await get_id_by_reply(msg)

    # edit the message with the id
    await msg.edit(
        text=text,
        reply_markup=await get_reply_markup(client),
    )


async def get_id_by_manage_business(_: Client, msg: types.Message):
    """
    Get id by manage business.
    """

    lang = repository.get_user_language(tg_id=msg.from_user.id)
    from_chat_id = msg.text.split("bizChat")[1]
    try:
        from_chat_id = int(from_chat_id)
    except ValueError:
        return
    await msg.reply(
        text=strings.get_text(key="ID_BY_MANAGE_BUSINESS", lang=lang).format(
            from_chat_id
        )
    )


async def handle_business_connection(
    client: Client, update: raw.types.UpdateBotBusinessConnect, users: dict
):
    """
    Handle business connection and disconnection
    """
    try:
        if not repository.is_user_exists(tg_id=update.connection.user_id):
            user = users.get(update.connection.user_id)
            repository.create_user(
                tg_id=user.id,
                name=user.first_name,
                username=user.username,
                language_code=user.language_code,
            )
        else:
            if not repository.is_active(tg_id=update.connection.user_id):
                repository.update_user(tg_id=update.connection.user_id, active=True)

        lang = repository.get_user_language(tg_id=update.connection.user_id)

        if not update.connection.disabled:  # user add the bot to our business
            if update.connection.can_reply:
                repository.update_user(
                    tg_id=update.connection.user_id,
                    business_id=update.connection.connection_id,
                )

                await client.send_message(
                    chat_id=update.connection.user_id,
                    text=strings.get_text(key="BUSINESS_CONNECTION", lang=lang),
                    message_effect_id=5107584321108051014,  # 👍
                )

            else:  # with no permission to reply
                await client.send_message(
                    chat_id=update.connection.user_id,
                    text=strings.get_text(
                        key="BUSINESS_CONNECTION_DISABLED", lang=lang
                    ),
                )

        else:  # user remove the bot from our business
            repository.update_user(tg_id=update.connection.user_id, business_id=None)

            await client.send_message(
                chat_id=update.connection.user_id,
                text=strings.get_text(key="BUSINESS_CONNECTION_REMOVED", lang=lang),
            )

    except Exception as e:
        _logger.exception(e)

    raise ContinuePropagation


async def send_about(_: Client, msg: types.Message):
    """Send info about the bot"""
    tg_id = msg.from_user.id
    lang = repository.get_user_language(tg_id=tg_id)

    await msg.reply_text(
        text=strings.get_text(key="INFO_ABOUT", lang=lang),
        quote=True,
        link_preview_options=types.LinkPreviewOptions(
            url="https://github.com/yehuda-lev/Get_Chat_ID_Bot",
            show_above_text=True,
        ),
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        text=strings.get_text(key="BUTTON_DEV", lang=lang),
                        url=strings.get_text(key="LINK_DEV", lang=lang),
                    )
                ],
            ]
        ),
    )


async def send_privacy_policy(_: Client, msg: types.Message):
    """Send privacy policy"""

    url = "https://telegra.ph/Privacy-Policy-for-GetChatID-IL-BOT-08-01"
    await msg.reply(
        text=url,
        link_preview_options=types.LinkPreviewOptions(
            show_above_text=True,
            prefer_large_media=True,
        ),
    )


async def get_raw(
    client: Client, update: raw.types.UpdateNewMessage, users: dict, __: dict
):
    """
    Handle raw updates
    """
    if isinstance(update, raw.types.UpdateBotBusinessConnect):
        # handle business connection
        await handle_business_connection(client, update, users)
