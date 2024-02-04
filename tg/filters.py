import re
import time

from pyrogram import types, filters

from db import filters as db_filters
from data import utils


settings = utils.get_settings()


def regex_start(arg: str):
    return filters.regex(rf"^/start ({arg})")


def create_user(_, __, msg: types.Message) -> bool:
    tg_id = msg.from_user.id
    name = msg.from_user.first_name + (
        " " + last if (last := msg.from_user.last_name) else ""
    )
    lang = l if (l := msg.from_user.language_code) == "he" else "en"

    if not db_filters.is_user_exists(tg_id=tg_id):
        db_filters.create_user(tg_id=tg_id, name=name, admin=False, lang=lang)
        return True

    if not db_filters.is_active(tg_id=tg_id):
        db_filters.change_active(tg_id=tg_id, active=True)

    return True


def is_not_raw(_, __, msg: types.Message) -> bool:
    if (
        msg.text
        or msg.game
        or msg.command
        or msg.photo
        or msg.document
        or msg.voice
        or msg.service
        or msg.media
        or msg.audio
        or msg.video
        or msg.contact
        or msg.location
        or msg.sticker
        or msg.poll
        or msg.animation
    ):
        return True
    return False


def is_force_reply(_, __, msg: types.Message) -> bool:
    if isinstance(msg.reply_to_message.reply_markup, types.ForceReply):
        return True
    return False


def is_admin(_, __, msg: types.Message) -> bool:
    tg_id = msg.from_user.id
    if db_filters.is_admin(tg_id=tg_id):
        return True
    return False


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


def query_lang(_, __, query: types.CallbackQuery) -> bool:
    if query.data == "he" or query.data == "en":
        return True
    return False


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

    return len(user_messages) < int(settings.LIMIT_SPAM)


def is_user_spamming(_, __, msg) -> bool:
    tg_id = msg.from_user.id
    return is_spamming(tg_id)

