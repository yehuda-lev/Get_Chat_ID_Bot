from pony.orm import db_session, select

from db.tables import Users


@db_session
def is_user_exists(tg_id: int) -> bool:
    return Users.exists(tg_id=str(tg_id))


@db_session
def get_user(tg_id: int) -> Users:
    return Users.get(tg_id=str(tg_id))


def is_active(tg_id: int) -> bool:
    return get_user(tg_id).active


def get_lang_by_user(tg_id: int) -> str:
    return get_user(tg_id=tg_id).lang


@db_session
def create_user(tg_id: int, name: str, admin=False, lang='he'):
    role = 'user' if not admin else 'admin'
    Users(tg_id=str(tg_id), name=name, role=role, lang=lang)


def is_admin(tg_id: int) -> bool:
    user = get_user(tg_id)
    if user.role == 'admin':
        return True
    return False


@db_session
def change_admin(tg_id: int, admin: bool):
    user = get_user(tg_id)
    role = 'admin' if admin else 'user'
    user.role = role


@db_session
def change_active(tg_id: int, active: bool):
    user = get_user(tg_id)
    user.active = active


@db_session
def change_lang(tg_id: int, lang: str):
    user = get_user(tg_id)
    user.lang = lang


@db_session
def get_users() -> list[Users]:
    return select(i.tg_id for i in Users)[:]


def get_tg_count() -> int:
    return len(get_users())


@db_session
def get_users_active() -> list[Users]:
    return select(i.tg_id for i in Users if i.active)[:]


# @db_session
def get_tg_active_count() -> int:
    return len(get_users_active())
