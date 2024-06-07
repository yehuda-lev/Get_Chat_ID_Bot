from pyrogram import Client, types


# TODO support of choose amount of payment


async def send_payment(_: Client, msg: types.Message):
    await msg.reply_invoice(
        title="Support me",
        description="Support me with 1 XTR",
        quote=True,
        payload=f"{msg.from_user.id}_bought",
        currency="XTR",  # telegram stars
        prices=[
            types.LabeledPrice(amount=1, label="star"),
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
        text=f"Thank you for supporting me with {payment.total_amount} {payment.currency}!",
        quote=True,
    )
