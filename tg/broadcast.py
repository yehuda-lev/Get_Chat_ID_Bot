from __future__ import annotations

import asyncio
import tempfile
from collections.abc import Awaitable, Callable, Sequence


class BroadcastStateError(RuntimeError):
    """Raised when the broadcast state is missing or invalid."""


class BroadcastCommandError(ValueError):
    """Raised when a broadcast command cannot be parsed."""


def get_broadcast_scope(state: dict | None) -> str:
    """
    Resolve the selected broadcast target from the listener state.
    """
    if not state:
        raise BroadcastStateError("Broadcast state is missing")

    scope = state.get("data")
    if scope not in {"users", "groups"}:
        raise BroadcastStateError(f"Unsupported broadcast scope: {scope!r}")

    return scope


def build_broadcast_log_file(text: str) -> str:
    """
    Persist the broadcast log text to a durable temporary file and return its path.
    """
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".log",
        delete=False,
    ) as temp_file:
        temp_file.write(text)
        temp_file.flush()
        return temp_file.name


def parse_delete_sent_id(message_text: str) -> str:
    """
    Parse the sent_id from a /delete command.
    """
    parts = (message_text or "").split(maxsplit=1)
    if not parts or not parts[0].startswith("/delete"):
        raise BroadcastCommandError("Not a delete command")

    if len(parts) < 2 or not parts[1].strip():
        raise BroadcastCommandError("Missing sent_id")

    return parts[1].strip()


async def broadcast_recipients(
    recipients: Sequence[object],
    deliver: Callable[[object], Awaitable[bool]],
    *,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    pace_after: int = 40,
    pace_pause: float = 3.0,
    inter_message_pause: float = 0.05,
    on_success: Callable[[object, int], Awaitable[None]] | None = None,
    on_failure: Callable[[object, int], Awaitable[None]] | None = None,
) -> tuple[int, int]:
    """
    Send a broadcast to recipients using async pacing.
    """
    sent = 0
    failed = 0
    batch_count = 0

    for recipient in recipients:
        if batch_count >= pace_after:
            batch_count = 0
            await sleep(pace_pause)

        is_sent = await deliver(recipient)
        if is_sent:
            sent += 1
            if on_success:
                await on_success(recipient, sent)
        else:
            failed += 1
            if on_failure:
                await on_failure(recipient, failed)

        batch_count += 1
        await sleep(inter_message_pause)

    return sent, failed


async def delete_broadcast_messages(
    messages: Sequence[object],
    delete_message: Callable[[int, int], Awaitable[bool]],
    *,
    delete_row: Callable[[int], Awaitable[None]] | None = None,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    pace_after: int = 40,
    pace_pause: float = 3.0,
    inter_message_pause: float = 0.05,
    on_progress: Callable[[int, int], Awaitable[None]] | None = None,
) -> tuple[int, int]:
    """
    Delete a broadcast delivery history with async pacing.
    """
    deleted = 0
    failed = 0
    batch_count = 0

    for sent_message in messages:
        if batch_count >= pace_after:
            batch_count = 0
            await sleep(pace_pause)

        is_deleted = await delete_message(sent_message.chat_id, sent_message.message_id)
        if is_deleted:
            deleted += 1
            if delete_row:
                await delete_row(sent_message.id)
        else:
            failed += 1

        if on_progress:
            await on_progress(deleted, failed)

        batch_count += 1
        await sleep(inter_message_pause)

    return deleted, failed
