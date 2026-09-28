import html
import logging
import re
import time

from pyrogram import types, filters, Client

from db import repository as db_filters
from data import config
from tg import others

_logger = logging.getLogger(__name__)

settings = config.get_settings()

user_id_to_state: dict[int, dict] = {}


def status_answer(params: dict = None) -> filters.Filter:
    """Check if user status is answer now"""

    if params is None:
        params = dict()

    async def get_is_answer(flt, _client: Client, msg: types.Message) -> bool:
        tg_id = msg.from_user.id
        user_statuses: dict = user_id_to_state.get(tg_id)

        if not user_statuses:
            return False

        return all(
            user_statuses.get(key, False) == value for key, value in flt.params.items()
        )

    return filters.create(get_is_answer, name="StatusAnswer", params=params)


def add_listener(*, tg_id: int, data: dict):
    """example: {1234567: {send_message_to_subscribers}}"""
    user_id_to_state.update({tg_id: data})


def remove_listener_by_tg_id(*, tg_id: int):
    try:
        user_id_to_state.pop(tg_id)
    except KeyError:
        pass


def start_command(command: str, prefixes: str | list = "/") -> filters.Filter:
    """
    Check if the message is a start command
        /start or https://t.me/bot?start=command
    Args:
        command: the command to check
        prefixes: the prefixes to check, default is "/"
    """

    def get_start_command(_, __, msg: types.Message) -> bool:
        text: str = msg.text or msg.caption
        if not text:
            return False

        for prefix in prefixes:
            if not text.startswith(prefix):
                continue

            without_prefix = text[len(prefix) :]

            text_command = without_prefix.split(" ")
            if len(text_command) > 1:  # "start link 1233455"
                return (
                    without_prefix[(len(text_command[0]) + 1) :].startswith(
                        command
                    )  # "start link 1233455
                    or text_command[0].startswith(command)  # "link 1233455"
                )
            else:
                return text_command[0].startswith(command)
        return False

    return filters.create(
        func=get_start_command,
        name="StartCommand",
        command=command,
        prefixes=prefixes,
    )


def create_user() -> filters.Filter:
    async def func(
        _,
        __,
        msg: (
            types.Message
            | types.InlineQuery
            | types.CallbackQuery
            | types.BusinessConnection
        ),
    ) -> bool:
        tg_user = (
            msg.from_user if not isinstance(msg, types.BusinessConnection) else msg.user
        )
        tg_id = tg_user.id
        name = tg_user.full_name if tg_user.full_name else ""

        user = await db_filters.get_user(tg_id=tg_id)
        if not user:
            try:
                created_by = (
                    msg.content.split(" ", maxsplit=1)[1]
                    if isinstance(msg, types.Message) and msg.content
                    else None
                )
            except IndexError:
                created_by = None

            await db_filters.create_user(
                tg_id=tg_id,
                name=name,
                admin=False,
                language_code=tg_user.language_code,
                created_by=created_by,
                username=tg_user.username,
            )
            return True

        if not user.active:
            await db_filters.update_user(tg_id=tg_id, active=True)

        if isinstance(msg, types.Message):
            others.UserLastMessage.add_user_last_message(
                user_id=tg_id, timestamp=msg.date
            )

        return True

    return filters.create(func, name="CreateUser")


def create_group() -> filters.Filter:
    async def func(_, __, msg: types.Message) -> bool:
        chat = msg.chat
        chat_id = chat.id
        name = chat.title if chat.title else ""

        group = await db_filters.get_group(group_id=chat_id)
        if not group:
            await db_filters.create_group(
                group_id=chat_id,
                name=name,
                username=chat.username,
            )
            return True

        return True

    return filters.create(func, name="CreateGroup")


def is_admin() -> filters.Filter:
    async def func(_, __, msg: types.Message) -> bool:
        return (await db_filters.get_user(tg_id=msg.from_user.id)).admin

    return filters.create(func, name="IsAdmin")


def get_usernames_and_ids(
    text: str, check_if_exists: bool = False
) -> tuple[list[str], dict[int, str]] | bool:
    """
    Get all usernames and ids from text/rich message
    Args:
        text: the text to check
        check_if_exists: if True, return True if any username or id exists, else return all usernames and ids
    """

    pattern = re.compile(
        # 1. HTML Tags (<a> or <tg-button>)
        r'<(?:a|tg-button)[^>]*?(?:href|url)=["\']tg://user\?id=(?P<html_id>\d+)["\'][^>]*?>(?P<html_name>.*?)</(?:a|tg-button)>|'
        # 2. Markdown Links: [Name](tg://user?id=123)
        r"\[(?P<md_name>[^\]]+)\]\(tg://user\?id=(?P<md_id>\d+)\)|"
        # 3. Raw IDs (Fallback if not inside a tag/markdown link)
        r"tg://user\?id=(?P<raw_id>\d+)|"
        # 4. Usernames with prefixes (@, t.me/, etc.)
        r"(?:@|(?:https?://)?(?:t\.me|telegram\.me|telegram\.dog)/|tg://resolve\?domain=)(?P<username_pre>[a-zA-Z][a-zA-Z0-9_]{2,})|"
        # 5. Usernames with suffixes (.t.me, etc.)
        r"(?P<username_suf>[a-zA-Z][a-zA-Z0-9_]{2,})\.(?:t\.me|telegram\.me|telegram\.dog)"
    )

    if check_if_exists:
        return bool(re.search(pattern, text))

    usernames = {}  # insertion order, deduplicated case-insensitively
    user_ids = {}  # unique user ids with names

    for match in pattern.finditer(text):
        groups = match.groupdict()

        if groups.get("html_id"):
            user_id = int(groups["html_id"])
            name = groups["html_name"]
            user_ids[user_id] = html.unescape(name)

        elif groups.get("md_id"):
            user_id = int(groups["md_id"])
            name = groups["md_name"]
            user_ids[user_id] = html.unescape(name)

        elif groups.get("raw_id"):
            user_id = int(groups["raw_id"])
            user_ids.setdefault(user_id, "❔")  # Preserve an existing display name

        elif groups.get("username_pre"):
            usernames.setdefault(groups["username_pre"].lower(), None)
        elif groups.get("username_suf"):
            usernames.setdefault(groups["username_suf"].lower(), None)

    return list(usernames), user_ids


def get_message_content(msg: types.Message, bot_username: str | None = None) -> str:
    """Read message content, excluding only the current bot's invocation."""
    content = msg.text or msg.caption or msg.rich_message
    text = content.markdown if content else ""
    if not bot_username:
        return text

    username = re.escape(bot_username)
    if msg.guest_query_id:
        text = re.sub(rf"^\s*@{username}\b\s*", "", text, count=1, flags=re.I)
    return re.sub(
        rf"^(\s*/(?:id|id_secret))@{username}\b",
        r"\1",
        text,
        count=1,
        flags=re.I,
    )


def is_username_or_ids(_, __, msg: types.Message | types.InlineQuery) -> bool:
    """
    Check if the message is a username by regex
    """
    if isinstance(msg, types.InlineQuery):
        text = msg.query
    else:
        text = get_message_content(msg)

    return get_usernames_and_ids(text, check_if_exists=True)


list_of_media_group = []


def is_media_group_exists(_, __, msg: types.Message) -> bool:
    media_group = msg.media_group_id

    if media_group not in list_of_media_group:
        list_of_media_group.append(media_group)
        return True
    return False


last_message_time = {}


def is_user_spamming() -> filters.Filter:
    """
    Check if the user is spamming
    Returns: True if the user is not spamming
    """

    async def func(_, __, msg: types.Message) -> bool:
        try:
            tg_id = msg.from_user.id
        except AttributeError:
            _logger.warning(
                f"Message {type(msg)} does not have from_user attribute - {msg}"
            )
            return False  # If the message does not have from_user, we cannot determine if it's spamming, so we return False

        current_time = time.time()

        user_messages = last_message_time.get(tg_id, [])

        # Remove messages older than 1 minute
        user_messages = [
            timestamp for timestamp in user_messages if current_time - timestamp <= 60
        ]

        # Update the message timestamps
        user_messages.append(current_time)
        last_message_time[tg_id] = user_messages

        return len(user_messages) < int(settings.limit_spam)

    return filters.create(func, name="IsUserSpamming")
