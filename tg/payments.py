import html
from pyrogram import Client, raw, types

from data import utils

TOKEN = utils.get_settings().TOKEN_PAYMENT

invoice = raw.types.Invoice(
    currency="EUR",
    prices=[
        raw.types.LabeledPrice(amount=100, label="asd 1"),
        # raw.types.LabeledPrice(amount=20000, label="asd 2"),
    ],
    test=True,
    name_requested=True,
    max_tip_amount=150000,
    suggested_tip_amounts=[200, 500, 1000, 1500],
)


async def send_payment(client: Client, msg: types.Message):
    r = await client.invoke(
        raw.functions.messages.SendMedia(
            peer=await client.resolve_peer(msg.from_user.id),
            media=raw.types.InputMediaInvoice(
                title="title",
                description="description",
                # photo=raw.types.InputWebDocument(
                #     url="https://telegram.org/file/464001019/11ed9/cJ2gxYh2KJs.29672/31f9128ef9c4794644",
                #     size=29672,
                #     mime_type="image/jpeg",
                #     attributes=[raw.types.DocumentAttributeImageSize(
                #         w=800,
                #         h=650
                #     )]
                # ),
                invoice=invoice,
                payload=f"{msg.from_user.id}_bought".encode(),
                provider=TOKEN,
                provider_data=raw.types.DataJSON(data="{}"),
                start_param="start_param",
            ),
            message="test",
            random_id=client.rnd_id(),
        )
    )
    print(r)


async def handle_shipping_query(client: Client, update: raw.types.UpdateBotShippingQuery):
    """
    Handle shipping queries.
    """
    print(f"handle_shipping_query: {update}")
    await client.send_message(
        chat_id=update.user_id,
        text=f"You've chosen an option.\n\n<b>Payload</b>:\n<code>{html.escape(str(update))}</code>",
    )
    r = await client.invoke(
        raw.functions.messages.SetBotShippingResults(
            query_id=update.query_id,
            shipping_options=[
                raw.types.ShippingOption(
                    id="asd_shipping",
                    title="Test Shipping Option",
                    prices=[
                        raw.types.LabeledPrice(amount=20000, label="asd"),
                    ],
                )
            ],
            error=None,
        )
    )
    print(r)


async def handle_pre_checkout_query(client: Client, update: raw.types.UpdateBotPrecheckoutQuery):
    """
    Handle pre-checkout queries.
    """
    print(f"handle_pre_checkout_query: {update}")
    await client.send_message(
        chat_id=update.user_id,
        text=f"You successfully bought something.\n\n<b>Payload</b>:\n<code>{html.escape(str(update))}</code>",
    )
    r = await client.invoke(
        raw.functions.messages.SetBotPrecheckoutResults(
            query_id=update.query_id,
            success=True,
            error=None,
        )
    )
    print(r)


async def handle_payment(client: Client, update: raw.types.UpdateNewMessage):
    """
    Handle payments.
    """
    print(f"handle_payment: {update}")
    if isinstance(update.message.action, raw.types.MessageActionPaymentSentMe):
        await client.send_message(
            chat_id=update.message.peer_id.user_id,
            text=f"You've paid {update.message.action.currency} {update.message.action.total_amount / 100:.2f} €"
                 f"Paid by {update.message.action.info.name}.",
        )
