import logging
import asyncio
import html
import re
import io
import time
import contextlib
import traceback

from pyrogram import Client, types, enums

from tg import utils

_logger = logging.getLogger(__name__)


async def run_exec(code: str, *args, timeout: int = None) -> str:
    exec(
        "async def __todo(client, msg, *args):\n"
        + " from pyrogram import raw\n"
        + " app = client\n"
        + " m = msg\n"
        + " r = m.reply_to_message\n"
        + " er = m.external_reply\n"
        + " u = m.from_user\n"
        + " ru = getattr(r, 'from_user', None)\n"
        + " here = getattr(m.chat, 'id', None)\n"
        + " p = print\n"
        + " async def get_raw(chat_id=None, msg_id=None):\n"
        + "   if not chat_id:\n"
        + "     chat_id = here\n"
        + "   if not msg_id:\n"
        + "     msg_id = m.id\n"
        + "   peer = await app.resolve_peer(chat_id)\n"
        + "   ids = [raw.types.InputMessageID(id=msg_id)]\n"
        + "   if isinstance(peer, raw.types.InputPeerChannel):\n"
        + "     rpc = raw.functions.channels.GetMessages(channel=peer, id=ids)\n"
        + "   else:\n"
        + "     rpc = raw.functions.messages.GetMessages(id=ids)\n"
        + "   return await app.invoke(rpc, sleep_threshold=-1)\n"
        + "".join(f"\n {_l}" for _l in code.split("\n"))
    )

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        await asyncio.wait_for(locals()["__todo"](*args), timeout=timeout)

    return f.getvalue()


code_result = (
    "🌐 **Language:**\n"
    "```{language}```\n\n"
    "💻 **Code:**\n"
    "```{pre_language}\n{code}\n```\n\n"
    "{result}"
)


async def python_exec(client: Client, msg: types.Message):
    if msg.from_user and msg.from_user.id != client.me.id:  # if send command to bot
        msg_to_edit = await msg.reply_text(
            "**✨ Executing...**",
            quote=True,
        )
    else:
        msg_to_edit = msg

    if len(msg.command) == 1 and msg.command[0] not in ("rpy", "rpyd"):
        return await msg_to_edit.edit_text("**Code to execute isn't provided**")

    if msg.command[0] == "rpy":
        reply = msg.reply_to_message
        if not (reply.text or reply.caption):
            return await msg_to_edit.edit_text("**Reply to a message with code**")
        code = reply.text or reply.caption

        # Check if msg is a reply to message with already executed code, and extract the code
        if code.startswith("🌐 Language:"):
            for entity in reply.entities or reply.caption_entities:
                if (
                    entity.type == enums.MessageEntityType.PRE
                    and entity.language == "python"
                ):
                    code = code[entity.offset : entity.offset + entity.length]
                    break

        else:
            if code.startswith("/py"):
                # ignore /py
                code = code.split(maxsplit=1)[1]
    else:
        code = (msg.text or msg.caption).split(maxsplit=1)[1]

    # fix character \u00A0
    code = code.replace("\u00a0", "").strip()

    await msg_to_edit.edit_text("**🔃 Executing...**")

    try:
        start_time = time.perf_counter()
        result = await run_exec(code, client, msg, timeout=60)
        stop_time = time.perf_counter()

        # Replace account phone number to anonymous
        if client.me.phone_number:
            result = result.replace(client.me.phone_number, "88806524973")

        if len(result) > 3072:
            new_result = html.escape(await utils.pate_code(result))
        elif re.match(r"^(https?):\/\/[^\s\/$.?#].[^\s]*$", result):
            new_result = html.escape(result)
        else:
            new_result = f"```python\n{html.escape(result)}```"

        text = code_result.format(
            language="Python",
            pre_language="python",
            code=html.escape(code),
            result=f"✨ **Result**:\n"
            f"{new_result}\n"
            f"**Completed in {round(stop_time - start_time, 5)}s.**",
        )
        await msg_to_edit.edit_text(
            text=text,
            link_preview_options=types.LinkPreviewOptions(is_disabled=True),
        )

    except asyncio.TimeoutError:
        return await msg_to_edit.edit_text(
            text=code_result.format(
                language="Python",
                pre_language="python",
                code=html.escape(code),
                result="**❌ Timeout Error!**",
            ),
            link_preview_options=types.LinkPreviewOptions(is_disabled=True),
        )
    except Exception as e:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            traceback.print_exc()

        # _logger.info(err.getvalue())

        return await msg_to_edit.edit_text(
            text=code_result.format(
                language="Python",
                pre_language="python",
                code=html.escape(code),
                result=f"**❌ {e.__class__.__name__}: {e}**\n"
                f"Traceback: {html.escape(await utils.pate_code(err.getvalue()))}",
            ),
            link_preview_options=types.LinkPreviewOptions(is_disabled=True),
        )
