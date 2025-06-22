import logging
from pyrogram import types, Client, errors, enums, ContinuePropagation

from data import cache_memory
from db import repository
from locales.translation_manager import TranslationKeys, manager
from tg import utils

_logger = logging.getLogger(__name__)


cache = cache_memory.cache_memory


async def settings(_: Client, msg: types.Message) -> None:
    """
    Show commands to change settings
    """
    user = await repository.get_user(tg_id=msg.from_user.id)
    lang = user.lang

    await msg.reply(
        text=manager.get_translation(TranslationKeys.SETTINGS, lang), quote=True
    )


async def send_about(_: Client, msg: types.Message):
    """Send info about the bot"""
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang

    await msg.reply_text(
        text=manager.get_translation(TranslationKeys.INFO_ABOUT, lang),
        quote=True,
        link_preview_options=types.LinkPreviewOptions(
            url="https://github.com/yehuda-lev/Get_Chat_ID_Bot",
            show_above_text=True,
        ),
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        text=manager.get_translation(TranslationKeys.BUTTON_DEV, lang),
                        url=manager.get_translation(TranslationKeys.LINK_DEV, lang),
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


async def choose_lang(_, msg: types.Message):
    """Choose language"""
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang

    await msg.reply(
        text=manager.get_translation(TranslationKeys.CHOICE_LANG, lang),
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        text=manager.get_translation(TranslationKeys.LANGUAGE, _lang),
                        callback_data=f"lang:{_lang}",
                    )
                    for _lang in langs
                ]
                for langs in [
                    utils.list_langs[i : i + 2]
                    for i in range(0, len(utils.list_langs), 2)
                ]
            ]
        ),
        quote=True,
    )


async def get_lang(_, query: types.CallbackQuery):
    """Get language"""
    data_lang = query.data.split(":")[1]
    tg_id = query.from_user.id
    await repository.update_user(tg_id=tg_id, lang=data_lang)
    await query.edit_message_text(
        text=manager.get_translation(TranslationKeys.DONE, data_lang).format(
            manager.get_translation(TranslationKeys.LANGUAGE, data_lang)
        ),
    )


async def handle_feature(_: Client, msg: types.Message | types.CallbackQuery):
    """
    Handle feature commands
    """
    tg_id = msg.from_user.id
    user = await repository.get_user(tg_id=tg_id)
    lang = user.lang

    copy_button = True
    multiple_chats = True
    if isinstance(msg, types.Message):
        if not user.feature:
            await repository.create_feature(user_id=tg_id)
            user = await repository.get_user(tg_id=tg_id)

        copy_button = user.feature.copy_button
        multiple_chats = user.feature.multiple_chats
    else:
        data = msg.data.split(":")
        if data[1] == "disable_all":
            copy_button = False
            multiple_chats = False
        elif data[1] == "enable_all":
            copy_button = True
            multiple_chats = True
        else:
            data_from_buttons = msg.message.reply_markup.inline_keyboard
            for btns in data_from_buttons:
                for btn in btns:
                    if btn.callback_data.startswith("feature:copy_button"):
                        copy_button = not btn.callback_data == "feature:copy_button-on"
                    elif btn.callback_data.startswith("feature:multiple_chats"):
                        multiple_chats = (
                            not btn.callback_data == "feature:multiple_chats-on"
                        )

            data = data[1].split("-")
            if data[0] == "copy_button":
                copy_button = not copy_button
            elif data[0] == "multiple_chats":
                multiple_chats = not multiple_chats

    inline_keyboard = [
        [
            types.InlineKeyboardButton(
                text=manager.get_translation(TranslationKeys.COPY_BUTTON, lang)
                + (" ✅" if copy_button else " ❌"),
                callback_data="feature:copy_button"
                + ("-on" if not copy_button else "-off"),
            ),
            types.InlineKeyboardButton(
                text=manager.get_translation(TranslationKeys.MULTIPLE_CHATS, lang)
                + (" ✅" if multiple_chats else " ❌"),
                callback_data="feature:multiple_chats"
                + ("-on" if not multiple_chats else "-off"),
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=manager.get_translation(
                    TranslationKeys.DISABLE_ALL_FEATURES, lang
                ),
                callback_data="feature:disable_all",
            )
        ],
        [
            types.InlineKeyboardButton(
                text=manager.get_translation(TranslationKeys.ENABLE_ALL_FEATURES, lang),
                callback_data="feature:enable_all",
            )
        ],
        [
            types.InlineKeyboardButton(
                text=manager.get_translation(TranslationKeys.SAVE_CHANGES, lang),
                callback_data=f"feature:save",
            )
        ],
    ]

    reply_markup = types.InlineKeyboardMarkup(inline_keyboard)
    if isinstance(msg, types.Message):
        await msg.reply(
            text=manager.get_translation(TranslationKeys.FEATURE_SETTINGS, lang),
            reply_markup=reply_markup,
            quote=True,
        )
        return

    data = msg.data.split(":")
    if not data[1] == "save":
        if reply_markup != msg.message.reply_markup:
            try:
                await msg.edit_message_reply_markup(reply_markup=reply_markup)
            except errors.MessageNotModified:
                pass
        else:
            await msg.answer()

    else:
        # save changes
        db_copy_button = user.feature.copy_button
        db_multiple_chats = user.feature.multiple_chats

        if copy_button != db_copy_button or multiple_chats != db_multiple_chats:
            await repository.update_feature(
                user_id=tg_id,
                feature_id=user.feature.id,
                **{
                    **(
                        {"copy_button": copy_button}
                        if copy_button != db_copy_button
                        else {}
                    ),
                    **(
                        {"multiple_chats": multiple_chats}
                        if multiple_chats != db_multiple_chats
                        else {}
                    ),
                },
            )
        await msg.edit_message_text(
            text=manager.get_translation(TranslationKeys.SETTINGS_SAVED, lang),
            reply_markup=None,
        )


async def added_to_group(_: Client, msg: types.Message):
    """
    Added the bot to the group
    """
    tg_id = msg.from_user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang

    await msg.reply(
        text=manager.get_translation(TranslationKeys.ADD_BOT_TO_GROUP, lang),
        quote=True,
        reply_markup=types.ReplyKeyboardMarkup(
            [
                [
                    types.KeyboardButton(
                        text=manager.get_translation(
                            TranslationKeys.BUTTON_ADD_BOT_TO_GROUP, lang
                        ),
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
            if not await repository.get_user(tg_id=update.from_user.id):
                _logger.debug(
                    f"The bot has been stopped by the user: {update.from_user.id}, {update.from_user.first_name}"
                )
                await repository.update_user(tg_id=update.from_user.id, active=False)
            return

    # the bot has had permissions removed from a chat
    if update.new_chat_member.user is None or not update.new_chat_member.user.is_self:
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
        await repository.update_group(group_id=update.chat.id, active=False)


async def handle_business_connection(
    client: Client,
    update: types.BusinessConnection,
):
    """
    Handle business connection and disconnection
    """
    tg_id = update.user.id
    db_user = await repository.get_user(tg_id=tg_id)
    lang = db_user.lang

    await repository.update_user(
        tg_id=tg_id,
        business_id=update.id if (update.is_enabled and update.can_reply) else None,
    )

    message_effect_id = None
    if update.is_enabled and update.can_reply:  # user add the bot to our business
        text = manager.get_translation(TranslationKeys.BUSINESS_CONNECTION, lang)
        message_effect_id = 5107584321108051014  # 👍

    elif update.is_enabled and not update.can_reply:  # with no permission to reply
        text = manager.get_translation(
            TranslationKeys.BUSINESS_CONNECTION_DISABLED, lang
        )

    else:  # user remove the bot from our business
        text = manager.get_translation(
            TranslationKeys.BUSINESS_CONNECTION_REMOVED, lang
        )

    await client.send_message(
        chat_id=tg_id,
        text=text,
        message_effect_id=message_effect_id,
    )

    raise ContinuePropagation
