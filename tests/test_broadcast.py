import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from tg import filters
from tg.admin_command import send_broadcast
from tg.broadcast import (
    BroadcastStateError,
    build_broadcast_log_file,
    broadcast_recipients,
    get_broadcast_scope,
)


def test_get_broadcast_scope_rejects_missing_state():
    with pytest.raises(BroadcastStateError):
        get_broadcast_scope(None)


def test_build_broadcast_log_file_writes_expected_text():
    path = build_broadcast_log_file("line one\nline two\n")
    try:
        assert Path(path).read_text(encoding="utf-8") == "line one\nline two\n"
    finally:
        Path(path).unlink(missing_ok=True)


def test_broadcast_recipients_uses_async_pacing_and_counts_successes():
    sleep_calls: list[float] = []
    delivered: list[str] = []

    async def fake_sleep(seconds: float):
        sleep_calls.append(seconds)

    async def deliver(recipient: str) -> bool:
        delivered.append(recipient)
        return recipient != "bad"

    sent, failed = asyncio.run(
        broadcast_recipients(
            ["a", "b", "bad"],
            deliver,
            sleep=fake_sleep,
            pace_after=2,
            pace_pause=3.0,
            inter_message_pause=0.1,
        )
    )

    assert sent == 2
    assert failed == 1
    assert delivered == ["a", "b", "bad"]
    assert sleep_calls == [0.1, 0.1, 3.0, 0.1]


def test_send_broadcast_without_state_replies_and_exits(monkeypatch):
    filters.user_id_to_state.clear()

    class FakeMsg:
        def __init__(self):
            self.from_user = SimpleNamespace(id=123)
            self.replies = []
            self.forward_origin = None

        async def reply(self, text, **kwargs):
            self.replies.append(text)
            return self

        async def reply_document(self, *args, **kwargs):  # pragma: no cover
            raise AssertionError("reply_document should not be called")

    fake_msg = FakeMsg()

    async def fail_if_called(*args, **kwargs):  # pragma: no cover
        raise AssertionError("repository should not be queried")

    monkeypatch.setattr("tg.admin_command.repository.get_all_users_active", fail_if_called)
    monkeypatch.setattr("tg.admin_command.repository.get_all_groups_active", fail_if_called)
    monkeypatch.setattr("tg.admin_command.repository.is_message_sent_exists", fail_if_called)

    asyncio.run(send_broadcast(None, fake_msg))

    assert fake_msg.replies
    assert "לא נמצא מצב שליחה פעיל" in fake_msg.replies[0]
    assert 123 not in filters.user_id_to_state
