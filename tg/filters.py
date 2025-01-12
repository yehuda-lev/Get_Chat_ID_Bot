import logging
import re
import time

from pyrogram import types, filters, enums, Client

from db import repository as db_filters
from data import config

_logger = logging.getLogger(__name__)

settings = config.get_settings()

user_id_to_state: dict[int:dict] = {}


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


def is_mention_users(msg: types.Message) -> bool:
    """
    Check if the message contains a mention
    """
    if msg.entities:
        return any(
            x
            for x in msg.entities
            if x.type == enums.MessageEntityType.MENTION
            or x.type == enums.MessageEntityType.TEXT_MENTION
        )
    return False


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
                    (msg.text or msg.caption).split(" ", maxsplit=1)[1]
                    if isinstance(msg, types.Message)
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


def get_username(text) -> str | None:
    """
    Check if is a username
    """
    username_regex = r"(?:@|t\.me\/|https:\/\/t\.me\/)([a-zA-Z][a-zA-Z0-9_]{2,})"

    match = re.search(username_regex, text)
    if match:
        return match.group(1)
    else:
        return None


def is_username(_, __, msg: types.Message | types.InlineQuery) -> bool:
    """
    Check if the message is a username by regex
    """
    if isinstance(msg, types.InlineQuery):
        text = msg.query
    else:
        text = msg.text
    return get_username(text) is not None


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
        tg_id = msg.from_user.id

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
