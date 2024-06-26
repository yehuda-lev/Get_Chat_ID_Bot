import logging
from pyrogram import Client, types

from tg import strings
from db import repository
from data import config

_logger = logging.getLogger(__name__)

settings = config.get_settings()


async def ask_for_payment(_: Client, msg: types.Message):
    tg_id = msg.from_user.id
    lang = repository.get_user_language(tg_id=tg_id)

    await msg.reply_text(
        text=strings.get_text(key="ASK_AMOUNT_TO_PAY", lang=lang),
        quote=True,
        message_effect_id=5159385139981059251,  # ❤️
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="⭐️ 5 XTR ️",
                        callback_data="stars:5",
                    ),
                    types.InlineKeyboardButton(
                        text="⭐️ 25 XTR",
                        callback_data="stars:25",
                    ),
                    types.InlineKeyboardButton(
                        text="⭐️ 100 XTR",
                        callback_data="stars:100",
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        text="⭐️ 150 XTR",
                        callback_data="stars:150",
                    ),
                    types.InlineKeyboardButton(
                        text="⭐️ 250 XTR",
                        callback_data="stars:250",
                    ),
                    types.InlineKeyboardButton(
                        text="⭐️ 400 XTR",
                        callback_data="stars:400",
                    ),
                ],
            ],
        ),
    )


async def send_payment(_: Client, cbd: types.CallbackQuery):
    tg_id = cbd.from_user.id
    lang = repository.get_user_language(tg_id=tg_id)
    amount = int(cbd.data.split(":")[1])

    await cbd.message.reply_invoice(
        title=strings.get_text(key="SUPPORT_ME", lang=lang),
        description=strings.get_text(key="TEXT_SUPPORT_ME", lang=lang).format(amount),
        payload=f"{tg_id}_bought",
        currency="XTR",  # telegram stars
        prices=[
            types.LabeledPrice(amount=amount, label="star"),
        ],
        provider_token=None,  # telegram stars
        message_effect_id=5159385139981059251,  # ❤️
    )


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
    lang = repository.get_user_language(tg_id=tg_id)
    payment = msg.successful_payment

    await msg.reply_text(
        text=strings.get_text(key="PAYMENT_SUCCESS", lang=lang).format(
            payment.total_amount
        ),
        quote=True,
        message_effect_id=5046509860389126442,  # 🎉
    )

    text_to_admin = (
        f"**🎉 תרומה חדשה 🎉**\n"
        f"מאת: __{msg.from_user.full_name}__\n"
        f"> מזהה: `{tg_id}`\n"
        f"> שם משתמש: @{msg.from_user.username}\n"
        f"> שפה: {lang}\n"
        f"סכום: {payment.total_amount} XTR ⭐️"
    )

    await client.send_message(
        chat_id=settings.admin_to_update_of_payment,
        text=text_to_admin,
        message_effect_id=5046509860389126442,  # 🎉
    )
