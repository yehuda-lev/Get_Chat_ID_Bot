import logging
from pyrogram import Client, types

from db import repository
from data import config
from locales.translation_manager import TranslationKeys, manager


_logger = logging.getLogger(__name__)

settings = config.get_settings()


async def ask_for_payment(_: Client, msg: types.Message):
    tg_id = msg.from_user.id
    lang = (await repository.get_user(tg_id=tg_id)).lang

    await msg.reply_text(
        text=manager.get_translation(TranslationKeys.ASK_AMOUNT_TO_PAY, lang),
        effect_id=5159385139981059251,  # ❤️
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="⭐️ 5",
                        callback_data="stars:5",
                    ),
                    types.InlineKeyboardButton(
                        text="⭐️ 25",
                        callback_data="stars:25",
                    ),
                    types.InlineKeyboardButton(
                        text="⭐️ 100",
                        callback_data="stars:100",
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        text="⭐️ 150",
                        callback_data="stars:150",
                    ),
                    types.InlineKeyboardButton(
                        text="⭐️ 250",
                        callback_data="stars:250",
                    ),
                    types.InlineKeyboardButton(
                        text="⭐️ 400",
                        callback_data="stars:400",
                    ),
                ],
            ],
        ),
    )


async def send_payment(client: Client, cbd: types.CallbackQuery):
    tg_id = cbd.from_user.id
    lang = (await repository.get_user(tg_id=tg_id)).lang
    amount = int(cbd.data.split(":")[1])

    await client.send_invoice(
        chat_id=tg_id,
        title=manager.get_translation(TranslationKeys.SUPPORT_ME, lang),
        description=manager.get_translation(
            TranslationKeys.TEXT_SUPPORT_ME, lang
        ).format(amount),
        payload=f"{tg_id}_bought",
        currency="XTR",  # telegram stars
        prices=[
            types.LabeledPrice(amount=amount, label="star"),
        ],
        provider_token=None,  # telegram stars
        message_effect_id=5159385139981059251,  # ❤️
    )

    # answer the callback query to remove the "spinning circle" on the button
    await cbd.answer()


async def confirm_payment(_: Client, query: types.PreCheckoutQuery):
    """
    send message service to user that payment is successful
    """
    await query.answer(ok=True)


async def send_thanks_for_support(client: Client, msg: types.Message):
    """
    send message to user that payment is successful, and thank you for support...
    """
    tg_id = msg.from_user.id
    lang = (await repository.get_user(tg_id=tg_id)).lang
    payment = msg.successful_payment

    await msg.reply_text(
        text=manager.get_translation(TranslationKeys.PAYMENT_SUCCESS, lang).format(
            payment.total_amount
        ),
        effect_id=5046509860389126442,  # 🎉
    )

    text_to_admin = (
        f"**🎉 תרומה חדשה 🎉**\n"
        f"מאת: __{msg.from_user.full_name}__\n"
        f"> מזהה: `{tg_id}`\n"
        f"> שם משתמש: @{msg.from_user.username}\n"
        f"> שפה: {lang}\n"
        f"סכום: {payment.total_amount} ⭐️"
    )

    await client.send_message(
        chat_id=settings.admin_to_update_of_payment,
        text=text_to_admin,
        effect_id=5046509860389126442,  # 🎉
    )
