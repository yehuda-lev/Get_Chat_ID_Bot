import re
import time

from pyrogram import types, filters, enums

from db import repository as db_filters
from data import config

settings = config.get_settings()

user_id_to_state: dict[int:dict] = {}


def status_answer(**kwargs) -> callable:
    """Check if user status is answer now"""

    def get_is_answer(_, __, msg: types.Message) -> bool:
        tg_id = msg.from_user.id
        exists = user_id_to_state.get(tg_id)
        if exists:
            return all(exists.get(key, False) == value for key, value in kwargs.items())
        return False

    return get_is_answer


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

            without_prefix = text[len(prefix):]

            text_command = without_prefix.split(" ")
            if len(text_command) > 1:
                return without_prefix[(len(text_command[0]) + 1):] == command
            else:
                return text_command[0] == command
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
    """""
    if msg.entities:
        return any(
            x for x in msg.entities
            if x.type == enums.MessageEntityType.MENTION
            or x.type == enums.MessageEntityType.TEXT_MENTION
        )
    return False


def create_user(_, __, msg: types.Message) -> bool:
    user = msg.from_user
    tg_id = user.id
    name = user.first_name + (" " + last if (last := user.last_name) else "")
    lang = lng if (lng := user.language_code) == "he" else "en"

    if not db_filters.is_user_exists(tg_id=tg_id):
        db_filters.create_user(tg_id=tg_id, name=name, admin=False, language_code=lang, username=user.username)
        return True

    if not db_filters.is_active(tg_id=tg_id):
        db_filters.update_user(tg_id=tg_id, active=True)

    return True


def is_admin(_, __, msg: types.Message) -> bool:
    tg_id = msg.from_user.id
    return db_filters.is_admin(tg_id=tg_id)


def check_username(text) -> str | None:
    """
    Check if is a username
    """
    username_regex = r"(?:@|t\.me\/|https:\/\/t\.me\/)([a-zA-Z][a-zA-Z0-9_]{2,})"

    match = re.search(username_regex, text)
    if match:
        return match.group(1)
    else:
        return None


def is_username(_, __, msg: types.Message) -> bool:
    return check_username(msg.text) is not None


list_of_media_group = []


def is_media_group_exists(_, __, msg: types.Message) -> bool:
    media_group = msg.media_group_id

    if media_group not in list_of_media_group:
        list_of_media_group.append(media_group)
        return True
    return False


last_message_time = {}


def is_spamming(tg_id: int) -> bool:
    """
    Check if the user is spamming
    """

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


def is_user_spamming(_, __, msg) -> bool:
    tg_id = msg.from_user.id
    return is_spamming(tg_id)
