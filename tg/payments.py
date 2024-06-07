from pyrogram import Client, types


async def ask_for_payment(_: Client, msg: types.Message):
    await msg.reply_text(
        text="How much do you want to donate?",
        quote=True,
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
    amount = int(cbd.data.split(":")[1])

    await cbd.message.reply_invoice(
        title="Support me",
        description=f"Support me with {amount} XTR ⭐️",
        payload=f"{cbd.from_user.id}_bought",
        currency="XTR",  # telegram stars
        prices=[
            types.LabeledPrice(amount=amount, label="star"),
        ],
        provider_token=None,  # telegram stars
    )


async def confirm_payment(_: Client, query: types.PreCheckoutQuery):
    """
    send message service to user that payment is successful
    """
    await query.answer(ok=True)


async def send_thanks_for_support(_: Client, msg: types.Message):
    """
    send message to user that payment is successful, and thank you for support...
    """
    payment = msg.successful_payment

    await msg.reply_text(
        text=f"Thank you for supporting me with {payment.total_amount} {payment.currency} ⭐️",
        quote=True,
    )
