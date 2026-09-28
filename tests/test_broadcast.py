import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from tg import filters
from tg.admin_command import delete_sent_messages, send_broadcast
from tg.broadcast import (
    BroadcastStateError,
    BroadcastCommandError,
    build_broadcast_log_file,
    broadcast_recipients,
    delete_broadcast_messages,
    get_broadcast_scope,
    parse_delete_sent_id,
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


def test_parse_delete_sent_id_extracts_the_identifier():
    assert parse_delete_sent_id("/delete abc123") == "abc123"
    assert parse_delete_sent_id("/delete@MyBot abc123") == "abc123"


def test_parse_delete_sent_id_rejects_missing_identifier():
    with pytest.raises(BroadcastCommandError):
        parse_delete_sent_id("/delete")


def test_delete_broadcast_messages_paces_and_removes_successful_rows():
    sleep_calls: list[float] = []
    deleted_rows: list[int] = []
    progress_updates: list[int] = []

    class Row:
        def __init__(self, row_id: int, chat_id: int, message_id: int):
            self.id = row_id
            self.chat_id = chat_id
            self.message_id = message_id

    async def fake_sleep(seconds: float):
        sleep_calls.append(seconds)

    async def delete_message(chat_id: int, message_id: int) -> bool:
        return message_id != 22

    async def delete_row(row_id: int):
        deleted_rows.append(row_id)

    async def track_progress(deleted: int, failed: int):
        progress_updates.append(deleted * 10 + failed)

    deleted, failed = asyncio.run(
        delete_broadcast_messages(
            [Row(1, 10, 11), Row(2, 10, 22), Row(3, 11, 33)],
            delete_message,
            delete_row=delete_row,
            sleep=fake_sleep,
            pace_after=2,
            pace_pause=2.5,
            inter_message_pause=0.2,
            on_progress=track_progress,
        )
    )

    assert deleted == 2
    assert failed == 1
    assert deleted_rows == [1, 3]
    assert progress_updates == [10, 11, 21]
    assert sleep_calls == [0.2, 0.2, 2.5, 0.2]


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

    monkeypatch.setattr(
        "tg.admin_command.repository.get_all_users_active", fail_if_called
    )
    monkeypatch.setattr(
        "tg.admin_command.repository.get_all_groups_active", fail_if_called
    )
    monkeypatch.setattr(
        "tg.admin_command.repository.is_message_sent_exists", fail_if_called
    )

    asyncio.run(send_broadcast(None, fake_msg))

    assert fake_msg.replies
    assert "לא נמצא מצב שליחה פעיל" in fake_msg.replies[0]
    assert 123 not in filters.user_id_to_state


def test_delete_sent_messages_deletes_rows_and_reports_progress(monkeypatch):
    class Row:
        def __init__(self, row_id: int, chat_id: int, message_id: int):
            self.id = row_id
            self.chat_id = chat_id
            self.message_id = message_id

    class FakeClient:
        def __init__(self):
            self.deleted = []

        async def delete_messages(self, chat_id, message_ids):
            self.deleted.append((chat_id, message_ids))

    class FakeMsg:
        def __init__(self):
            self.text = "/delete sent123"
            self.replies = []

        async def reply(self, text, **kwargs):
            self.replies.append(text)
            return self

    rows = [Row(1, 10, 11), Row(2, 20, 22)]
    deleted_rows: list[int] = []
    fake_client = FakeClient()
    fake_msg = FakeMsg()

    async def exists(*, sent_id):
        return sent_id == "sent123"

    async def get_messages_sent(*, sent_id):
        assert sent_id == "sent123"
        return rows

    async def delete_row(message_sent_id):
        deleted_rows.append(message_sent_id)

    monkeypatch.setattr("tg.admin_command.repository.is_message_sent_exists", exists)
    monkeypatch.setattr(
        "tg.admin_command.repository.get_messages_sent", get_messages_sent
    )
    monkeypatch.setattr("tg.admin_command.repository.delete_message_sent", delete_row)

    asyncio.run(delete_sent_messages(fake_client, fake_msg))

    assert fake_client.deleted == [(10, 11), (20, 22)]
    assert deleted_rows == [1, 2]
    assert fake_msg.replies[0] == "מוחק 2 הודעות שנשלחו"
    assert fake_msg.replies[-1] == "נמחקו 2 הודעות, נכשלו 0 הודעות"
