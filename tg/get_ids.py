import logging
import random
from typing import Tuple

from pyrogram import Client, types, enums, errors

from data import clients
from tg import filters, utils
from db import repository
from db.repository import StatsType
from locales.translation_manager import manager, TranslationKeys, get_button_with_emoji

_logger = logging.getLogger(__name__)


async def welcome(_: Client, msg: types.Message):
    """start the bot"""
    user = msg.from_user
    tg_id = user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang

    # https://t.me/tgbetachat/1939059 not works for old versions
    request_multiple_chats = (
        10 if not db_user.feature or db_user.feature.multiple_chats else 1
    )

    await msg.reply(
        text=manager.get_translation(TranslationKeys.WELCOME, lang).format(
            user.mention(user.full_name),
            " ".join(
                manager.get_translation(TranslationKeys.LANGUAGE, _lang).split(" ")[1]
                for _lang in utils.list_langs
            ),
        ),
        link_preview_options=types.LinkPreviewOptions(is_disabled=True),
        reply_markup=types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            placeholder=manager.get_translation(TranslationKeys.CHOSE_CHAT_TYPE, lang),
            keyboard=[
                [
                    # user
                    get_button_with_emoji(
                        key=TranslationKeys.USER,
                        lang=lang,
                        request_users=types.KeyboardButtonRequestUsers(
                            button_id=1,
                            user_is_bot=False,
                            max_quantity=request_multiple_chats,
                            request_name=True,
                            request_username=True,
                        ),
                    ),
                    # bot
                    get_button_with_emoji(
                        key=TranslationKeys.BOT,
                        lang=lang,
                        request_users=types.KeyboardButtonRequestUsers(
                            button_id=2,
                            user_is_bot=True,
                            max_quantity=request_multiple_chats,
                            request_name=True,
                            request_username=True,
                        ),
                    ),
                ],
                [
                    # group
                    get_button_with_emoji(
                        key=TranslationKeys.GROUP,
                        lang=lang,
                        request_chat=types.KeyboardButtonRequestChat(
                            button_id=3,
                            chat_is_channel=False,
                            request_title=True,
                            request_username=True,
                        ),
                    ),
                    # channel
                    get_button_with_emoji(
                        key=TranslationKeys.CHANNEL,
                        lang=lang,
                        request_chat=types.KeyboardButtonRequestChat(
                            button_id=4,
                            chat_is_channel=True,
                            request_title=True,
                            request_username=True,
                        ),
                    ),
                ],
            ],
        ),
    )

    await msg.answer(
        text="![🪪](tg://emoji?id=5422683699130933153)",
        effect_id=5046509860389126442,  # 🎉
        disable_notification=True,
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    get_button_with_emoji(
                        key=TranslationKeys.INFO_MENU,
                        lang=lang,
                        callback_data="help:menu:welcome:menu",
                    )
                ],
            ],
        ),
    )


async def get_chats_manager(_: Client, msg: types.Message):
    """Get chats manager"""
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang
    text = manager.get_translation(TranslationKeys.CHAT_MANAGER, lang)

    await msg.reply(
        text=text,
        link_preview_options=types.LinkPreviewOptions(is_disabled=True),
        reply_markup=types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            placeholder=manager.get_translation(TranslationKeys.CHOSE_CHAT_TYPE, lang),
            keyboard=[
                [
                    # group
                    get_button_with_emoji(
                        key=TranslationKeys.GROUP,
                        lang=lang,
                        request_chat=types.KeyboardButtonRequestChat(
                            button_id=3,
                            chat_is_channel=False,
                            request_title=True,
                            request_username=True,
                            user_administrator_rights=types.ChatPrivileges(
                                can_manage_chat=True
                            ),
                        ),
                    ),
                    # channel
                    get_button_with_emoji(
                        key=TranslationKeys.CHANNEL,
                        lang=lang,
                        request_chat=types.KeyboardButtonRequestChat(
                            button_id=4,
                            chat_is_channel=True,
                            request_title=True,
                            request_username=True,
                            user_administrator_rights=types.ChatPrivileges(
                                can_manage_chat=True
                            ),
                        ),
                    ),
                ],
            ],
        ),
    )


async def get_forward(_: Client, msg: types.Message):
    """Get message forward"""
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang
    inline_keyboard: list[list[types.InlineKeyboardButton] | None] = []
    forward = msg.forward_origin
    chat_id = None

    if isinstance(
        forward,
        (types.MessageOriginUser, types.MessageOriginChat, types.MessageOriginChannel),
    ):
        if isinstance(forward, types.MessageOriginUser):
            chat = forward.sender_user
            chat_id = chat.id
            name = chat.full_name if chat.full_name else ""
            format_name = utils.format_chat_name(name, chat.username)
            text = manager.get_translation(TranslationKeys.ID_USER, lang).format(
                format_name,
                chat_id,
            )
        else:
            chat = (
                forward.sender_chat
                if isinstance(forward, types.MessageOriginChat)
                else forward.chat
            )
            chat_id = chat.id
            name = chat.title if chat.title else ""
            format_name = utils.format_chat_name(name, chat.username)
            text = manager.get_translation(
                TranslationKeys.ID_CHANNEL_OR_GROUP, lang
            ).format(
                format_name,
                chat_id,
            )

    elif isinstance(forward, types.MessageOriginHiddenUser):
        # The user hides the forwarding of a message from him or Deleted Account
        name = forward.sender_user_name
        text = manager.get_translation(TranslationKeys.ID_HIDDEN, lang).format(
            utils.format_chat_name(name)
        )
        inline_keyboard.append(
            [
                get_button_with_emoji(
                    key="Help 🆘",
                    lang=lang,
                    url="https://t.me/GetChatID_Updates/29",
                )
            ]
        )
    else:
        return

    await msg.reply(
        text=text,
        reply_markup=utils.get_buttons(
            chat_id=chat_id,
            name=name,
            lang=lang,
            user=db_user,
            inline_buttons=inline_keyboard,
        ),
    )

    utils.create_stats(
        type_stats=StatsType.FORWARD_MESSAGE, lang=msg.from_user.language_code
    )


async def get_me(_: Client, msg: types.Message):
    """Get id the user"""
    user = msg.from_user
    tg_id = user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang
    name = user.full_name if user.full_name else ""
    format_name = utils.format_chat_name(name, user.username)

    await msg.reply(
        text=manager.get_translation(TranslationKeys.ID_USER, lang).format(
            format_name, tg_id
        ),
        reply_markup=utils.get_buttons(
            chat_id=tg_id, name=name, lang=lang, user=db_user
        ),
    )

    utils.create_stats(type_stats=StatsType.ME, lang=msg.from_user.language_code)


async def get_contact(_: Client, msg: types.Message):
    """Get id from contact"""
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang
    chat_id, name = None, None

    if msg.contact.user_id:
        contact = msg.contact
        chat_id = contact.user_id
        name = contact.first_name + (
            (" " + contact.last_name) if contact.last_name else ""
        )

        text = manager.get_translation(TranslationKeys.ID_USER, lang).format(
            utils.format_chat_name(name),
            chat_id,
        )

    else:
        text = manager.get_translation(TranslationKeys.NOT_HAVE_ID, lang)
    await msg.reply(
        text=text,
        reply_markup=utils.get_buttons(
            chat_id=chat_id, name=name, lang=lang, user=db_user
        ),
    )

    utils.create_stats(type_stats=StatsType.CONTACT, lang=msg.from_user.language_code)


async def get_request_peer(_: Client, msg: types.Message):
    """ "Get request peer"""
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang
    inline_keyboard: list[list[types.InlineKeyboardButton] | None] = []
    reply_markup = None
    chat_id = None
    name = None

    if msg.users_shared:
        users = msg.users_shared.users
        if len(users) == 1:
            user = users[0]
            chat_id = user.id
            name = user.full_name if user.full_name else ""
            format_name = utils.format_chat_name(name, user.username)
            text = manager.get_translation(TranslationKeys.ID_USER, lang).format(
                format_name,
                chat_id,
            )

        else:  # support of multiple users
            text_lang = manager.get_translation(TranslationKeys.ID_USER, lang)
            text = ""
            for user in users:
                name = user.full_name if user.full_name else ""
                format_name = utils.format_chat_name(name, user.username)
                text += f"{text_lang.format(format_name, user.id)}\n"

            # button copy chat id
            if db_user.feature and db_user.feature.copy_button:
                for user in users:
                    user_id = user.id
                    inline_keyboard.append(
                        [
                            types.InlineKeyboardButton(
                                text=user.full_name if user.full_name else "",
                                copy_text=types.CopyTextButton(text=str(user_id)),
                            ),
                            *utils.get_buttons_link_to_chat(chat_id=user_id),
                        ]
                    )

    elif msg.chat_shared:
        request_chat = msg.chat_shared
        chat = request_chat.chat

        if request_chat.button_id == 100:  # support of added to group
            if not await repository.get_group(group_id=chat.id):
                await repository.create_group(
                    group_id=chat.id,
                    name=chat.title,
                    username=chat.username,
                    added_by_id=tg_id,
                )
            else:
                await repository.update_group(
                    group_id=chat.id, added_by_id=tg_id, active=True
                )

            text = manager.get_translation(
                TranslationKeys.BOT_ADDED_TO_GROUP, lang
            ).format(
                f"[{chat.title}](t.me/c/{str(chat.id).replace('-100', '')}/1000000000)",
                chat.id,
            )
            reply_markup = types.ReplyKeyboardRemove()

        else:
            name = chat.title
            format_name = utils.format_chat_name(name, chat.username)
            chat_id = chat.id
            text = manager.get_translation(
                TranslationKeys.ID_CHANNEL_OR_GROUP, lang
            ).format(format_name, chat_id)

    else:
        return

    await msg.reply(
        text=text,
        reply_markup=utils.get_buttons(
            chat_id=chat_id,
            name=name,
            lang=lang,
            user=db_user,
            inline_buttons=inline_keyboard,
            reply_markup=reply_markup,
        ),
    )

    utils.create_stats(
        type_stats=StatsType.BUTTON_SHARE_CHAT, lang=msg.from_user.language_code
    )


async def get_story(_: Client, msg: types.Message):
    """Get id from story"""
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang
    chat = msg.story.chat
    chat_id = chat.id

    if chat.type in [
        enums.ChatType.PRIVATE,  # user
        enums.ChatType.BOT,  # bot (when it's possible to upload story with bot)
    ]:
        name = chat.full_name if chat.full_name else ""
        format_name = utils.format_chat_name(name, chat.username)
        text = manager.get_translation(TranslationKeys.ID_USER, lang).format(
            format_name,
            chat_id,
        )
    elif chat.type in [
        enums.ChatType.CHANNEL,  # channel
        enums.ChatType.SUPERGROUP,  # supergroup
        enums.ChatType.GROUP,  # group
    ]:
        name = chat.title
        format_name = utils.format_chat_name(name, chat.username)
        text = manager.get_translation(
            TranslationKeys.ID_CHANNEL_OR_GROUP, lang
        ).format(format_name, chat_id)
    else:
        return

    await msg.reply(
        text=text,
        reply_markup=utils.get_buttons(
            chat_id=chat_id, name=name, lang=lang, user=db_user
        ),
    )

    utils.create_stats(type_stats=StatsType.STORY, lang=msg.from_user.language_code)


async def get_via_bot(_: Client, msg: types.Message):
    """Get id via bot"""

    tg_id = msg.from_user.id
    name = msg.via_bot.first_name
    format_name = utils.format_chat_name(name, msg.via_bot.username)
    chat_id = msg.via_bot.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang
    text = manager.get_translation(TranslationKeys.ID_USER, lang).format(
        format_name, chat_id
    )

    await msg.reply(
        text=text,
        reply_markup=utils.get_buttons(
            chat_id=chat_id,
            name=name,
            lang=lang,
            user=db_user,
        ),
    )

    utils.create_stats(type_stats=StatsType.VIA_BOT, lang=msg.from_user.language_code)


# search username


async def get_users_from_text(
    content: str, lang: str, *, include_unresolved_username: bool = True
) -> tuple[str, dict[int, str]]:
    """Resolve the first username and return display text plus IDs for buttons.

    Additional embedded IDs stay out of the text. On lookup failure, optionally
    identify the attempted username; without one, use the generic fallback.
    """
    usernames, user_ids = filters.get_usernames_and_ids(text=content)
    username = (
        usernames[0] if usernames else None
    )  # Limit to just one username to avoid flood.
    chat = None

    # define the text to return if no chat is found
    if username and include_unresolved_username:
        text = manager.get_translation(
            TranslationKeys.CAN_NOT_GET_USERNAME_ID, lang
        ).format(username=utils.format_chat_name(f"@{username}"))
    else:
        text = manager.get_translation(TranslationKeys.CAN_NOT_GET_THE_ID, lang)

    if username:
        client_search: Client = random.choice((clients.bot_1, clients.bot_2))
        try:
            chat = await client_search.get_chat(username, force_full=False)
        except errors.BadRequest:  # username not found
            pass

        except errors.FloodWait:
            if client_search.name == clients.bot_1.name:
                client_search = clients.bot_2
            else:
                client_search = clients.bot_1

            try:
                chat = await client_search.get_chat(username, force_full=False)
            except Exception as e:  # noqa
                _logger.error(f"Error in get_chat with {client_search.name}: {e}")

    if isinstance(chat, types.Chat):
        name = chat.title if chat.title else chat.full_name if chat.full_name else ""
        chat_id = chat.id
        user_ids.pop(chat_id, None)
        user_ids = {chat_id: name, **user_ids}

        name = utils.format_chat_name(name, username)

        if chat.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
            text = manager.get_translation(TranslationKeys.ID_USER, lang).format(
                name, chat_id
            )

        else:
            text = manager.get_translation(
                TranslationKeys.ID_CHANNEL_OR_GROUP, lang
            ).format(name, chat_id)

    return text, user_ids


async def extract_users_from_message(client: Client, msg: types.Message):
    """Get id from username or link by message"""

    lang, db_user = None, None
    if msg.from_user:
        tg_id = msg.from_user.id
        db_user = await repository.get_user(tg_id=tg_id)
        lang = db_user.lang if db_user else msg.from_user.language_code
    lang = lang or "en"

    content = filters.get_message_content(msg, client.me.username)
    text, user_ids = await get_users_from_text(content=content, lang=lang)

    buttons = utils.get_buttons(
        chat_id=list(user_ids.keys()),
        name=list(user_ids.values()),
        lang=lang,
        user=db_user,
        send_alert=msg.chat is not None and msg.chat.type == enums.ChatType.PRIVATE,
        by=(
            "guest_mode"
            if msg.guest_query_id
            else "group"
            if (
                msg.chat
                and msg.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP)
            )
            else None
        ),
    )

    if msg.guest_query_id:
        await client.answer_guest_query(
            guest_query_id=msg.guest_query_id,
            result=types.InlineQueryResultArticle(
                title=text,
                input_message_content=types.InputTextMessageContent(
                    message_text=text,
                ),
                reply_markup=buttons,
            ),
        )
    else:
        await msg.reply(
            text=text,
            reply_markup=buttons,
        )

    utils.create_stats(type_stats=StatsType.SEARCH_USERNAME, lang=lang)


async def ask_inline_query(_: Client, msg: types.Message):
    """
    Ask inline query
    """
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang

    await msg.reply(
        text=manager.get_translation(TranslationKeys.ASK_INLINE_QUERY, lang),
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        text="🔍",
                        switch_inline_query_current_chat="",
                        icon_custom_emoji_id=5832251986635920010,
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="🔍",
                        switch_inline_query="",
                        icon_custom_emoji_id=5877468380125990242,
                    )
                ],
            ],
        ),
    )

    utils.create_stats(
        type_stats=StatsType.ASK_INLINE_QUERY, lang=msg.from_user.language_code
    )


async def get_username_by_inline_query(_: Client, query: types.InlineQuery):
    """
    Get id by inline query
    """

    db_user = await repository.get_user(tg_id=query.from_user.id)
    lang = db_user.lang

    text, user_ids = await get_users_from_text(content=query.query, lang=lang)
    chat_id = list(user_ids.keys())[0] if user_ids else None
    name = list(user_ids.values())[0] if user_ids else None

    try:
        await query.answer(
            results=[
                types.InlineQueryResultArticle(
                    title=f"{name} • `{chat_id}`",
                    id="1",
                    input_message_content=types.InputTextMessageContent(
                        message_text=text,
                    ),
                    reply_markup=utils.get_buttons(
                        chat_id=chat_id,
                        name=name,
                        lang=lang,
                        user=db_user,
                        by="inline_query",
                        send_alert=False,
                    ),
                ),
            ],
            cache_time=5,
        )
    except errors.BadRequest as e:
        _logger.error(f"Can't answer to inline query {e}")

    utils.create_stats(
        type_stats=StatsType.SEARCH_INLINE, lang=query.from_user.language_code
    )


# reply to


parse_info = Tuple[str | None, int | None, str | None]


def parse_reply_to_another_chat(lang: str, msg: types.Message) -> parse_info:
    """
    Get id by reply to another chat,
    if the message sent in a group than return the id and name of the group,
    """
    text, chat_id, name = None, None, None

    reply_to = msg.external_reply.origin

    if isinstance(reply_to, types.MessageOriginUser):  # user
        user = reply_to.sender_user
        chat_id = user.id
        name = user.full_name
        format_name = utils.format_chat_name(name, user.username)
        if lang:
            text = manager.get_translation(TranslationKeys.ID_USER, lang).format(
                format_name,
                chat_id,
            )
    elif isinstance(reply_to, types.MessageOriginChat):  # group
        group = reply_to.sender_chat
        chat_id = group.id
        name = group.title
        format_name = utils.format_chat_name(name, group.username)
        if lang:
            text = manager.get_translation(
                TranslationKeys.ID_CHANNEL_OR_GROUP, lang
            ).format(format_name, chat_id)
    elif isinstance(reply_to, types.MessageOriginChannel):  # channel
        channel = reply_to.chat
        chat_id = channel.id
        name = channel.title
        format_name = utils.format_chat_name(name, channel.username)
        if lang:
            text = manager.get_translation(
                TranslationKeys.ID_CHANNEL_OR_GROUP, lang
            ).format(format_name, chat_id)
    elif isinstance(reply_to, types.MessageOriginHiddenUser):
        # The user hides the forwarding of a message from him or Deleted Account
        name = reply_to.sender_user_name
        if lang:
            text = manager.get_translation(TranslationKeys.ID_HIDDEN, lang).format(
                utils.format_chat_name(name)
            )

    return text, chat_id, name


def parse_reply_to_message(lang: str, msg: types.Message) -> parse_info:
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
        format_name = utils.format_chat_name(name, chat.username)
        if lang:
            text = manager.get_translation(TranslationKeys.ID_USER, lang).format(
                format_name, chat_id
            )
    elif msg.reply_to_message.sender_chat:
        chat = msg.reply_to_message.sender_chat
        chat_id = chat.id
        name = chat.title
        format_name = utils.format_chat_name(name, chat.username)
        if lang:
            text = manager.get_translation(
                TranslationKeys.ID_CHANNEL_OR_GROUP, lang
            ).format(format_name, chat_id)

    return text, chat_id, name


def parse_reply_to_story(lang: str, msg: types.Message) -> parse_info:
    """
    Get id by reply to story
    """
    text, chat_id, name = None, None, None
    story = msg.reply_to_story
    if story.chat.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
        chat = story.chat
        chat_id = chat.id
        name = chat.full_name if chat.full_name else ""
        format_name = utils.format_chat_name(name, chat.username)

        if lang:
            text = manager.get_translation(TranslationKeys.ID_USER, lang).format(
                format_name, chat_id
            )
    elif story.chat.type in (
        enums.ChatType.CHANNEL,
        enums.ChatType.GROUP,
        enums.ChatType.SUPERGROUP,
    ):
        chat = story.chat
        chat_id = chat.id
        name = chat.title
        format_name = utils.format_chat_name(name, chat.username)
        if lang:
            text = manager.get_translation(
                TranslationKeys.ID_CHANNEL_OR_GROUP, lang
            ).format(format_name, chat_id)

    return text, chat_id, name


def parse_reply(lang: str | None, msg: types.Message) -> parse_info:
    """
    Get id by all reply types
    """
    if msg.reply_to_story:
        return parse_reply_to_story(lang, msg)

    elif msg.reply_to_message:
        return parse_reply_to_message(lang, msg)

    # reply to another chat
    elif msg.external_reply:
        return parse_reply_to_another_chat(lang, msg)

    else:
        chat = msg.chat
        chat_id = chat.id
        name = chat.full_name or chat.title or ""
        format_name = utils.format_chat_name(name, chat.username)

        text = None
        if lang:
            text = manager.get_translation(
                TranslationKeys.ID_CHANNEL_OR_GROUP, lang
            ).format(format_name, chat_id)

        return text, chat_id, name


async def get_ids_in_the_group_and_guest_mode(client: Client, msg: types.Message):
    """
    get ids in the group
    """
    chat_id, name, lang, db_user, text, tg_id = None, None, None, None, None, None
    if msg.from_user:
        tg_id = msg.from_user.id
        db_user = await repository.get_user(tg_id=tg_id)
        lang = db_user.lang if db_user else msg.from_user.language_code

    lang = lang or "en"
    is_guest_mode = msg.guest_query_id

    content = filters.get_message_content(msg, client.me.username)

    if filters.get_usernames_and_ids(
        text=content, check_if_exists=True
    ):  # get is mention users
        try:
            await extract_users_from_message(client, msg)
        except errors.RPCError as e:
            _logger.error(f"Telegram error in reply message in the group: {e}")
            await client.leave_chat(chat_id=msg.chat.id)
            return
        except Exception:
            _logger.exception("Error processing reply message in the group")
            return

        stats_type = (
            StatsType.ID_BY_GUEST_MODE if is_guest_mode else StatsType.ID_IN_GROUP
        )
        utils.create_stats(type_stats=stats_type, lang=lang)
        return

    if not name and not chat_id:  # get reply to chat id
        text, chat_id, name = parse_reply(lang, msg)

    if not name:
        return

    buttons = utils.get_buttons(
        chat_id=chat_id,
        name=name,
        lang=lang,
        user=db_user,
        by="group" if not is_guest_mode else "guest_mode",
        send_alert=False,
    )
    if not text:
        text = utils.format_chat_name(name)
        if chat_id:
            text += f" • `{chat_id}`"

    if not is_guest_mode:
        try:
            await msg.reply(
                text=text,
                reply_markup=buttons,
            )
        except errors.RPCError as e:
            _logger.error(f"Telegram error in reply message in the group: {e}")
            await client.leave_chat(chat_id=msg.chat.id)
            return
        except Exception:
            _logger.exception("Error processing reply message in the group")
            return

        stats_type = (
            StatsType.ID_IN_GROUP
            if not msg.ephemeral_message_id
            else StatsType.ID_FOR_EPHEMERAL_COMMAND
        )
        utils.create_stats(type_stats=stats_type, lang=lang)

    else:
        try:
            await client.answer_guest_query(
                guest_query_id=msg.guest_query_id,
                result=types.InlineQueryResultArticle(
                    title=text,
                    input_message_content=types.InputTextMessageContent(
                        message_text=text,
                    ),
                    reply_markup=buttons,
                ),
            )
        except Exception as e:
            _logger.error(f"Error in answer to guest query: {e}")

        utils.create_stats(type_stats=StatsType.ID_BY_GUEST_MODE, lang=lang)


async def get_reply_to_another_chat(_: Client, msg: types.Message):
    """
    get reply to another chat
    """
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang

    text, chat_id, name = parse_reply_to_another_chat(lang, msg)

    if not text:
        return

    await msg.reply(
        text=text,
        reply_markup=utils.get_buttons(
            chat_id=chat_id,
            name=name,
            lang=lang,
            user=db_user,
        ),
    )

    utils.create_stats(type_stats=StatsType.REPLY_TO_ANOTHER_CHAT, lang=lang)


# business connection


async def get_id_with_business_connection(_: Client, msg: types.Message):
    """
    Get id with business connection.
    """
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang

    text, chat_id, name = parse_reply(lang, msg)

    # edit the message with the id
    await msg.edit(
        text=text,
        reply_markup=utils.get_buttons(
            chat_id=chat_id,
            name=name,
            lang=lang,
            user=db_user,
            by="business_connection",
            send_alert=False,
        ),
    )

    utils.create_stats(type_stats=StatsType.BUSINESS_ID, lang=lang)


async def get_id_by_manage_business(_: Client, msg: types.Message):
    """
    Get id by manage business.
    """
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang
    from_chat_id = msg.text.split("bizChat")[1]
    try:
        from_chat_id = int(from_chat_id)
    except ValueError:
        return
    await msg.reply(
        text=manager.get_translation(
            TranslationKeys.ID_BY_MANAGE_BUSINESS, lang
        ).format(from_chat_id),
        reply_markup=utils.get_buttons(
            chat_id=from_chat_id,
            name=from_chat_id,
            lang=lang,
            user=db_user,
        ),
    )

    utils.create_stats(
        type_stats=StatsType.BUSINESS_SETTINGS, lang=msg.from_user.language_code
    )
