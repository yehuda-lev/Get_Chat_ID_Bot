from pyrogram import types

from db import filters as db_filters


def create_user(_, __, msg: types.Message) -> bool:
    tg_id = msg.from_user.id
    name = msg.from_user.first_name + \
        (" " + last if (last := msg.from_user.last_name) else "")
    lang = l if (l := msg.from_user.language_code) == 'he' else 'en'

    if not db_filters.is_user_exists(tg_id=tg_id):
        db_filters.create_user(tg_id=tg_id, name=name, admin=False, lang=lang)
        return True

    if not db_filters.is_active(tg_id=tg_id):
        db_filters.change_active(tg_id=tg_id, active=True)

    return True


def is_not_raw(_, __, msg: types.Message) -> bool:
    if msg.text or msg.game or msg.command or msg.photo or msg.document or msg.voice \
            or msg.service or msg.media or msg.audio or msg.video or msg.contact \
            or msg.location or msg.sticker or msg.poll or msg.animation:
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


def query_lang(_, __, query: types.CallbackQuery) -> bool:
    if query.data == 'he' or query.data == 'en':
        return True
    return False
