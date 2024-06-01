from pyrogram import Client, raw, types


# TODO support of choose amount of payment

async def send_payment(client: Client, msg: types.Message):
    await client.invoke(
        raw.functions.messages.SendMedia(
            peer=await client.resolve_peer(msg.from_user.id),
            media=raw.types.InputMediaInvoice(
                title="Support me",
                description="Support me with 1 XTR",
                invoice=raw.types.Invoice(
                    currency="XTR",  # telegram stars
                    prices=[
                        raw.types.LabeledPrice(amount=1, label="asd 1"),
                    ],
                ),
                payload=f"{msg.from_user.id}_bought".encode(),
                provider=None,  # telegram stars
                provider_data=raw.types.DataJSON(data="{}"),
            ),
            message="Support me with 1 XTR",
            random_id=client.rnd_id(),
        )
    )


async def confirm_payment(
    client: Client, update: raw.types.UpdateBotPrecheckoutQuery
):
    """
    send message service to user that payment is successful
    """

    await client.invoke(
        raw.functions.messages.SetBotPrecheckoutResults(
            query_id=update.query_id,
            success=True,
        )
    )


async def send_thanks_for_support(client: Client, update: raw.types.UpdateNewMessage):
    """
    send message to user that payment is successful, and thank you for support...
    """
    payments: raw.types.MessageActionPaymentSentMe = update.message.action
    await client.send_message(
        chat_id=update.message.peer_id.user_id,
        reply_parameters=types.ReplyParameters(message_id=update.message.id),
        text=f"Thank you for supporting me with {payments.total_amount} XTR!",
    )
