from pony.orm import db_session, select

from db.tables import Users
from db.cashe_memory import MemoryCache

cache = MemoryCache()


@cache.cachable(cache_name="is_user_exists", params="tg_id")
@db_session
def is_user_exists(*, tg_id: int) -> bool:
    """Check if user exists in DB or not"""
    return Users.exists(tg_id=str(tg_id))


@cache.cachable(cache_name="is_active", params="tg_id")
@db_session
def is_active(*, tg_id: int) -> bool:
    """Check if user active or not."""
    return Users.get(tg_id=str(tg_id)).active


@cache.cachable(cache_name="get_lang_by_user", params="tg_id")
@db_session
def get_lang_by_user(*, tg_id: int) -> str:
    """Get lang user"""
    return Users.get(tg_id=str(tg_id)).lang


@cache.invalidate(cache_name="is_user_exists", params="tg_id")
@db_session
def create_user(*, tg_id: int, name: str, admin=False, lang="he"):
    """create a new user in DB"""
    role = "user" if not admin else "admin"
    Users(tg_id=str(tg_id), name=name, role=role, lang=lang)


@cache.cachable(cache_name="is_admin", params="tg_id")
@db_session
def is_admin(*, tg_id: int) -> bool:
    """Check if user admin or not"""
    user = Users.get(tg_id=str(tg_id))
    if user.role == "admin":
        return True
    return False


@cache.invalidate(cache_name="is_admin", params="tg_id")
@db_session
def change_admin(*, tg_id: int, admin: bool):
    """change user admin"""
    user = Users.get(tg_id=str(tg_id))
    role = "admin" if admin else "user"
    user.role = role


@cache.invalidate(cache_name="is_active", params="tg_id")
@db_session
def change_active(*, tg_id: int, active: bool):
    """Change active user"""
    user = Users.get(tg_id=str(tg_id))
    user.active = active


@cache.invalidate(cache_name="get_lang_by_user", params="tg_id")
@db_session
def change_lang(*, tg_id: int, lang: str):
    """Change user lang"""
    user = Users.get(tg_id=str(tg_id))
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
