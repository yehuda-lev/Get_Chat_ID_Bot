import logging
from pyrogram import types, Client, errors

from data import cache_memory
from db import repository
from locales.translation_manager import TranslationKeys, manager


_logger = logging.getLogger(__name__)


cache = cache_memory.cache_memory


async def settings(_: Client, msg: types.Message) -> None:
    """
    Show commands to change settings
    """
    user = await repository.get_user(tg_id=msg.from_user.id)
    lang = user.lang

    # text = manager.get_translation(TranslationKeys.SETTINGS, lang)
    text = "settings"
    await msg.reply(text, quote=True)


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
                text="Copy Button" + (" ✅" if copy_button else " ❌"),
                callback_data="feature:copy_button"
                + ("-on" if not copy_button else "-off"),
            ),
            types.InlineKeyboardButton(
                text="Multiple Chats" + (" ✅" if multiple_chats else " ❌"),
                callback_data="feature:multiple_chats"
                + ("-on" if not multiple_chats else "-off"),
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="Disable All Features",
                callback_data="feature:disable_all",
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Enable All Features",
                callback_data="feature:enable_all",
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Save Changes",
                callback_data=f"feature:save",
            )
        ],
    ]

    reply_markup = types.InlineKeyboardMarkup(inline_keyboard)
    if isinstance(msg, types.Message):
        await msg.reply(
            text="feature settings",
            reply_markup=reply_markup,
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
            text="Feature settings saved successfully.",
            reply_markup=None,
        )
