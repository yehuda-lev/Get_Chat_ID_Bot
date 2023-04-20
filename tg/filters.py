from pyrogram import filters, types

from db import filters as db_filters


def create_user(_, __, msg: types.Message) -> bool:
    tg_id = msg.from_user.id
    name = msg.from_user.first_name + \
        (" " + last if (last := msg.from_user.last_name) else "")

    if not db_filters.is_user_exists(tg_id):
        db_filters.create_user(tg_id=tg_id, name=name, admin=False)
    return True


def is_admin(_, __, msg: types.Message) -> bool:
    tg_id = msg.from_user.id
    if db_filters.is_admin(tg_id):
        return True
    return False

