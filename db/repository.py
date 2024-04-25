# this file contains all the database operations

import datetime
import logging
from sqlalchemy import exists, func

from db.tables import get_session, User, Group, MessageSent
from data import cashe_memory


_logger = logging.getLogger(__name__)

cache = cashe_memory.cache_memory


# user


def is_user_exists(*, tg_id: int) -> bool:
    """Check if user exists in DB or not"""

    with get_session() as session:
        return session.query(exists().where(User.tg_id == tg_id)).scalar()


def is_active(*, tg_id: int) -> bool:
    """Check if user active or not."""

    with get_session() as session:
        return session.query(User.active).filter(User.tg_id == tg_id).scalar()


def is_admin(*, tg_id: int) -> bool:
    """Check if user admin or not"""

    with get_session() as session:
        return session.query(User.admin).filter(User.tg_id == tg_id).scalar()


def get_lang_by_user(*, tg_id: int) -> str:
    """Get lang user"""

    with get_session() as session:
        return session.query(User.language_code).filter(User.tg_id == tg_id).scalar()


def create_user(
    *,
    tg_id: int,
    name: str,
    username: str = None,
    language_code: str = "en",
    admin: bool = False,
    active: bool = True,
):
    """
    Create tg user
    :param tg_id: the user id
    :param name: the name of user
    :param username: the username of user
    :param language_code: the language code of user
    :param admin: is admin or not, default is False
    :param active: is active or not, default is True
    """

    _logger.debug(
        f"Create user: tg_id:{tg_id}, name:{name}, username:{username}, "
        f"language_code:{language_code}, is_admin:{admin}, active:{active}"
    )

    with get_session() as session:
        user = User(
            tg_id=tg_id,
            name=name,
            username=username,
            language_code=language_code,
            admin=admin,
            active=active,
            created_at=datetime.datetime.now(),
        )
        session.add(user)
        session.commit()


def update_user(*, tg_id: int, **kwargs):
    """
    Update user
    :param tg_id: the user id
    :param kwargs: the data to update
    """
    _logger.debug(f"Update user: tg_id:{tg_id}, data:{kwargs}")
    with get_session() as session:
        session.query(User).filter(User.tg_id == tg_id).update(kwargs)
        session.commit()


def get_user(*, tg_id: int) -> User:
    """
    Get user by tg id
    :param tg_id: the user id
    :return: :class:`Group`
    """

    with get_session() as session:
        return session.query(User).filter(User.tg_id == tg_id).one()


# group


def is_group_exists(*, group_id: int) -> bool:
    """Check if group exists or not"""

    with get_session() as session:
        return session.query(exists().where(Group.group_id == group_id)).scalar()


def create_group(
    *,
    group_id: int,
    name: str,
    username: str = None,
    added_by_id: int,
    active: bool = True,
):
    """
    Create group
    :param group_id: the group id
    :param name: the name of group
    :param username: the username of group
    :param added_by_id: the user id who add the group
    :param active: is active or not, default is True
    """

    _logger.debug(
        f"Create group: group_id:{group_id}, name:{name}, "
        f"username:{username}, added_by_id:{added_by_id}, active:{active}"
    )

    with get_session() as session:
        user = get_user(tg_id=added_by_id)
        group = Group(
            group_id=group_id,
            name=name,
            username=username,
            created_at=datetime.datetime.now(),
            added_by=user,
            active=active,
        )
        session.add(group)
        session.commit()


def update_group(*, group_id: int, **kwargs):
    """
    Update group
    :param group_id: the group id
    :param kwargs: the data to update
    """

    _logger.debug(f"Update group: group_id:{group_id}, data:{kwargs}")
    with get_session() as session:
        session.query(Group).filter(Group.group_id == group_id).update(kwargs)
        session.commit()


def get_group(*, group_id: int) -> Group:
    """
    Get group by group id
    :param group_id: the group id
    :return: :class:`Group`,
    """

    with get_session() as session:
        return session.query(Group).filter(Group.group_id == group_id).one()


# stats


def get_all_users_count() -> int:
    """Get all users count"""

    with get_session() as session:
        return session.query(func.count(User.id)).scalar()


def get_users_count_active() -> int:
    """Get all active users count"""

    with get_session() as session:
        return session.query(func.count(User.id)).filter(User.active == True).scalar()


def get_all_users_active() -> list[User]:
    """Get all active users"""

    with get_session() as session:
        return session.query(User).filter(User.active == True).all()


def get_all_groups_count() -> int:
    """Get all groups count"""

    with get_session() as session:
        return session.query(func.count(Group.id)).scalar()


def get_groups_count_active() -> int:
    """Get all active groups count"""

    with get_session() as session:
        return session.query(func.count(Group.id)).filter(Group.active == True).scalar()


def get_all_groups_active() -> list[Group]:
    """Get all active groups"""

    with get_session() as session:
        return session.query(Group).filter(Group.active == True).all()


# message_sent


def create_message_sent(*, sent_id: str, chat_id: int, message_id: int) -> MessageSent:
    """Create message sent
    :param sent_id: the sent id
    :param chat_id: the chat id
    :param message_id: the message id
    :return: :class:`MessageSent`
    """

    _logger.debug(
        f"Create message sent: sent_id:{sent_id}, chat_id:{chat_id}, message_id:{message_id}"
    )

    with get_session() as session:
        message_sent = MessageSent(
            sent_id=sent_id,
            chat_id=chat_id,
            message_id=message_id,
            sent_at=datetime.datetime.now(),
        )
        session.add(message_sent)
        session.commit()
        return message_sent


def get_messages_sent(*, sent_id: str) -> list[MessageSent]:
    """Get messages sent by sent_id
    :param sent_id: the sent id
    :return: list of :class:`MessageSent`
    """

    with get_session() as session:
        return session.query(MessageSent).filter(MessageSent.sent_id == sent_id).all()


def is_message_sent_exists(*, sent_id: str) -> bool:
    """
    Check if message sent exists
    :param sent_id: the sent id
    :return: bool
    """

    with get_session() as session:
        return session.query(exists().where(MessageSent.sent_id == sent_id)).scalar()
