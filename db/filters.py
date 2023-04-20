from pony.orm import db_session

from tables import Users


@db_session
def is_user_exists(tg_id: int) -> bool:
    return Users.exists(tg_id=str(tg_id))


@db_session
def create_user(tg_id: int, name: str, is_admin=False):
    role = 'user' if not is_admin else 'admin'
    Users(tg_id=str(tg_id), name=name, role=role)



