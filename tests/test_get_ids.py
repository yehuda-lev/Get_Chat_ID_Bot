"""Regression tests for ID extraction, buttons, and message formatting.

Run with the project's Python environment: python -m pytest tests/test_get_ids.py -q
For one failure, append ::test_name to the file path and use -v for more detail.
Each test sets up an example, calls the real function, then checks the expected
behavior with assert. Read the failing assertion and pytest's actual/expected
diff first; fix the application unless the intended behavior has changed.
@pytest.mark.parametrize runs the same test for every listed example.
"""

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, Mock

import pytest
from pyrogram import enums, errors, types
from pyrogram.parser import Parser

from tg import filters, get_ids, utils
from locales.translation_manager import manager, TranslationKeys


@pytest.fixture(autouse=True)
def isolate_io(monkeypatch):
    # Replace handler I/O with test doubles; no Telegram requests are sent.
    # AsyncMock records awaited calls. return_value supplies a result; side_effect
    # can raise an error. monkeypatch restores the originals after each test.
    monkeypatch.setattr(get_ids.repository, "get_user", AsyncMock(return_value=None))
    monkeypatch.setattr(utils, "create_stats", Mock())
    monkeypatch.setattr(utils, "send_alert_to_change_settings", AsyncMock())
    monkeypatch.setattr(
        get_ids.clients.bot_1,
        "get_chat",
        AsyncMock(side_effect=AssertionError("Unexpected lookup")),
    )
    monkeypatch.setattr(
        get_ids.clients.bot_2,
        "get_chat",
        AsyncMock(side_effect=AssertionError("Unexpected lookup")),
    )
    monkeypatch.setattr(get_ids.clients.bot_1, "me", NS(username="TestBot"))
    monkeypatch.setattr(get_ids.random, "choice", lambda clients: clients[0])


def message(text="/id", *, guest=False, anonymous=False):
    # NS is a small object with only the message fields used by these handlers.
    return NS(
        text=NS(markdown=text) if text else None,
        caption=None,
        rich_message=None,
        from_user=None if anonymous else NS(id=1, language_code="en"),
        chat=NS(id=-100123, type=enums.ChatType.SUPERGROUP),
        guest_query_id=123 if guest else None,
        ephemeral_message_id=None,
        reply=AsyncMock(),
    )


# Extraction: choose usernames predictably and keep extra IDs out of reply text.
def test_extraction_preserves_order_and_normalizes_ids():
    usernames, ids = filters.get_usernames_and_ids(
        "@Zulu @ALICE @zulu [Alice](tg://user?id=00123) tg://user?id=123"
    )
    assert usernames == ["zulu", "alice"]
    assert ids == {123: "Alice"}


@pytest.mark.parametrize(
    "content,guest,expected",
    [
        ("@TESTBOT @Alice @TestBot", True, "@Alice @TestBot"),
        ("@TestBotExtra @Alice", True, "@TestBotExtra @Alice"),
        ("/id@TestBot @Alice", False, "/id @Alice"),
        ("@TestBot", False, "@TestBot"),
        ("", True, ""),
    ],
)
def test_message_content_removes_only_invocation(content, guest, expected):
    assert (
        filters.get_message_content(message(content, guest=guest), "TestBot")
        == expected
    )


def test_ids_only_do_not_echo_input_or_expose_extra_ids():
    text, ids = asyncio.run(
        get_ids.get_users_from_text("[Alice](tg://user?id=12345)", "en")
    )
    assert ids == {12345: "Alice"}
    assert text == manager.get_translation(TranslationKeys.CAN_NOT_GET_THE_ID, "en")


@pytest.mark.parametrize("include_name", [True, False])
def test_failed_username_has_optional_named_error(include_name):
    get_ids.clients.bot_1.get_chat.side_effect = errors.UsernameNotOccupied()
    text, ids = asyncio.run(
        get_ids.get_users_from_text(
            "@al__ice [Alice](tg://user?id=12345)",
            "en",
            include_unresolved_username=include_name,
        )
    )
    # The username must survive Telegram's parser, including Markdown delimiters.
    rendered = asyncio.run(Parser(None).parse(text))["message"]
    assert ("@al__ice" in rendered) is include_name
    assert ids == {12345: "Alice"}
    assert "12345" not in text


def test_resolved_username_is_first_and_deduplicated():
    get_ids.clients.bot_1.get_chat.side_effect = None
    get_ids.clients.bot_1.get_chat.return_value = types.Chat(
        id=12345, type=enums.ChatType.PRIVATE, first_name="Alice", username="alice"
    )
    text, ids = asyncio.run(
        get_ids.get_users_from_text(
            "@Alice @Zulu [Duplicate](tg://user?id=12345) [Extra](tg://user?id=99999)",
            "en",
        )
    )
    assert list(ids) == [12345, 99999]
    assert "12345" in text and "99999" not in text
    get_ids.clients.bot_1.get_chat.assert_awaited_once_with("alice", force_full=False)


def test_flood_uses_second_client():
    get_ids.clients.bot_1.get_chat.side_effect = errors.FloodWait(10)
    get_ids.clients.bot_2.get_chat.side_effect = None
    get_ids.clients.bot_2.get_chat.return_value = types.Chat(
        id=123, type=enums.ChatType.PRIVATE, first_name="Alice"
    )
    text, ids = asyncio.run(get_ids.get_users_from_text("@Alice", "en"))
    assert 123 in ids and "123" in text
    get_ids.clients.bot_2.get_chat.assert_awaited_once_with("alice", force_full=False)


# Buttons: enabled by default; an explicit user preference disables copies.
def test_disabled_copy_buttons_hide_list_ids():
    user = NS(feature=NS(copy_button=False))
    assert utils.get_buttons([123, 456], ["Alice", "Bob"], "en", user=user) is None


def test_scalar_without_copy_keeps_valid_links():
    user = NS(feature=NS(copy_button=False))
    markup = utils.get_buttons(123, "Alice", "en", user=user)
    assert markup.inline_keyboard[0][0].url == "tg://openmessage?user_id=123"


def test_missing_user_and_credit_are_supported():
    markup = utils.get_buttons(123, "Alice", "en", user=None, by="group")
    assert markup.inline_keyboard[0][0].copy_text.text == "123"
    assert markup.inline_keyboard[1][0].url == "tg://openmessage?user_id=123"
    assert markup.inline_keyboard[-1][0].url.endswith("start=start_group")


@pytest.mark.parametrize("user", [None, NS(feature=None)])
def test_copy_buttons_are_enabled_without_saved_preferences(user):
    markup = utils.get_buttons(
        [123, 456], ["Alice", "Bob"], "en", user=user, send_alert=False
    )
    copies = [
        button.copy_text.text
        for row in markup.inline_keyboard
        for button in row
        if button.copy_text
    ]
    assert copies == ["123", "456"]


def test_no_ids_produce_no_empty_keyboard():
    assert (
        utils.get_buttons([], [], "en", user=NS(feature=NS(copy_button=True))) is None
    )


def test_copy_buttons_keep_all_extracted_ids():
    markup = utils.get_buttons(
        [123, 456], ["Alice", "Bob"], "en", user=NS(feature=NS(copy_button=True))
    )
    assert [row[0].copy_text.text for row in markup.inline_keyboard] == ["123", "456"]


@pytest.mark.parametrize("username", [None, "al__ice"])
def test_format_name_survives_telegram_parser(username):
    # Test the rendered result, not just the markup string we generate.
    name = "Alice </a> & **bold** [x](https://example.com) `code` --Admin-- --Open"
    formatted = utils.format_chat_name(name, username)
    parsed = asyncio.run(Parser(None).parse(formatted))
    assert parsed["message"] == name
    entities = parsed["entities"] or []
    assert len(entities) == (1 if username else 0)
    if username:
        assert entities[0].url == f"https://t.me/{username}"


def test_contact_does_not_need_username():
    get_ids.repository.get_user.return_value = NS(
        lang="en", feature=NS(copy_button=True)
    )
    msg = message()
    msg.contact = types.Contact(phone_number="0", first_name="Alice", user_id=123)
    asyncio.run(get_ids.get_contact(None, msg))
    assert "123" in msg.reply.call_args.kwargs["text"]


@pytest.mark.parametrize("anonymous", [False, True])
def test_group_extraction_supports_unregistered_and_anonymous_senders(anonymous):
    msg = message("/id [Alice](tg://user?id=123)", anonymous=anonymous)
    client = NS(me=NS(username="TestBot"), leave_chat=AsyncMock())
    asyncio.run(get_ids.get_ids_in_the_group_and_guest_mode(client, msg))
    msg.reply.assert_awaited_once()
    client.leave_chat.assert_not_awaited()


def test_guest_invocation_only_uses_reply_target(monkeypatch):
    msg = message("@TestBot /id", guest=True)
    client = NS(
        me=NS(username="TestBot"),
        answer_guest_query=AsyncMock(),
        leave_chat=AsyncMock(),
    )
    parse_reply = Mock(return_value=("Alice • 123", 123, "Alice"))
    monkeypatch.setattr(get_ids, "parse_reply", parse_reply)
    asyncio.run(get_ids.get_ids_in_the_group_and_guest_mode(client, msg))
    parse_reply.assert_called_once()
    client.answer_guest_query.assert_awaited_once()
    client.leave_chat.assert_not_awaited()


@pytest.mark.parametrize("route", ["extraction", "reply"])
@pytest.mark.parametrize(
    "error,should_leave",
    [
        pytest.param(errors.ChatWriteForbidden(), True, id="telegram-error"),
        pytest.param(ValueError("bad input"), False, id="processing-error"),
    ],
)
def test_group_leaves_only_on_telegram_errors(monkeypatch, route, error, should_leave):
    # Both ways of answering must distinguish Telegram RPC errors from local
    # errors. Inject the failure without making a real request or leaving a chat.
    msg = message("/id @Alice" if route == "extraction" else "/id")
    if route == "extraction":
        monkeypatch.setattr(
            get_ids, "extract_users_from_message", AsyncMock(side_effect=error)
        )
    else:
        monkeypatch.setattr(
            get_ids, "parse_reply", Mock(return_value=("Alice • 123", 123, "Alice"))
        )
        msg.reply.side_effect = error
    client = NS(me=NS(username="TestBot"), leave_chat=AsyncMock())
    asyncio.run(get_ids.get_ids_in_the_group_and_guest_mode(client, msg))
    if should_leave:
        client.leave_chat.assert_awaited_once_with(chat_id=msg.chat.id)
    else:
        client.leave_chat.assert_not_awaited()
    utils.create_stats.assert_not_called()  # Failed replies are not successful actions.


def test_hidden_reply_preserves_localized_text_and_literal_name():
    name = "Alice --Admin--"
    msg = message()
    msg.reply_to_story = msg.reply_to_message = None
    msg.external_reply = NS(
        origin=types.MessageOriginHiddenUser(
            date=None,
            sender_user_name=name,
        )
    )
    client = NS(me=NS(username="TestBot"), leave_chat=AsyncMock())
    asyncio.run(get_ids.get_ids_in_the_group_and_guest_mode(client, msg))
    parsed = asyncio.run(Parser(None).parse(msg.reply.call_args.kwargs["text"]))
    assert "The ID is hidden" in parsed["message"]
    assert name in parsed["message"]


def test_hidden_forward_preserves_literal_name():
    get_ids.repository.get_user.return_value = NS(
        lang="en", feature=NS(copy_button=True)
    )
    name = "Alice --Admin--"
    msg = message()
    msg.forward_origin = types.MessageOriginHiddenUser(date=None, sender_user_name=name)
    asyncio.run(get_ids.get_forward(None, msg))
    parsed = asyncio.run(Parser(None).parse(msg.reply.call_args.kwargs["text"]))
    assert name in parsed["message"]


@pytest.mark.parametrize("lang", utils.list_langs)
def test_named_error_translated_for_every_language(lang):
    # Read each JSON directly so English fallback cannot hide a missing translation.
    path = Path(__file__).resolve().parents[1] / "locales" / f"{lang}.json"
    translations = json.loads(path.read_text())
    template = translations["CAN_NOT_GET_USERNAME_ID"]
    assert "{username}" in template
    assert "@alice" in template.format(username="@alice")
