# this file contains all the database operations

import datetime
import logging
from sqlalchemy import exists, func

from db.tables import get_session, User, Group, MessageSent, StatsType, Stats
from data import cache_memory


_logger = logging.getLogger(__name__)

cache = cache_memory.cache_memory


# user


@cache.cachable(cache_name="is_user_exists", params="tg_id")
def is_user_exists(*, tg_id: int) -> bool:
    """Check if user exists in DB or not"""

    with get_session() as session:
        return session.query(exists().where(User.tg_id == tg_id)).scalar()  # noqa


@cache.cachable(cache_name="is_active", params="tg_id")
def is_active(*, tg_id: int) -> bool:
    """Check if user active or not."""

    with get_session() as session:
        return session.query(User.active).filter(User.tg_id == tg_id).scalar()


@cache.cachable(cache_name="is_admin", params="tg_id")
def is_admin(*, tg_id: int) -> bool:
    """Check if user admin or not"""

    with get_session() as session:
        return session.query(User.admin).filter(User.tg_id == tg_id).scalar()


def create_user(
    *,
    tg_id: int,
    name: str,
    username: str = None,
    language_code: str,
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

    _logger.debug(f"Create user: {tg_id=}, {name=}, {username=}, {language_code=}")

    # delete the cache
    cache.delete("is_user_exists", cache_id=cache.build_cache_id(tg_id=tg_id))
    cache.delete("is_active", cache_id=cache.build_cache_id(tg_id=tg_id))
    cache.delete("is_admin", cache_id=cache.build_cache_id(tg_id=tg_id))
    cache.delete("get_user", cache_id=cache.build_cache_id(tg_id=tg_id))
    cache.delete("get_user_language", cache_id=cache.build_cache_id(tg_id=tg_id))

    with get_session() as session:
        user = User(
            tg_id=tg_id,
            name=name,
            username=username,
            language_code=language_code,
            lang=language_code,
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

    _logger.debug(f"Update user: {tg_id=}, {kwargs=}")

    # delete the cache
    cache.delete("is_user_exists", cache_id=cache.build_cache_id(tg_id=tg_id))
    cache.delete("is_active", cache_id=cache.build_cache_id(tg_id=tg_id))
    cache.delete("is_admin", cache_id=cache.build_cache_id(tg_id=tg_id))
    cache.delete("get_user", cache_id=cache.build_cache_id(tg_id=tg_id))
    cache.delete("get_user_language", cache_id=cache.build_cache_id(tg_id=tg_id))

    with get_session() as session:
        session.query(User).filter(User.tg_id == tg_id).update(kwargs)
        session.commit()


@cache.cachable(cache_name="get_user", params="tg_id")
def get_user(*, tg_id: int) -> User:
    """
    Get user by tg id
    :param tg_id: the user id
    :return: :class:`Group`
    """

    with get_session() as session:
        return session.query(User).filter(User.tg_id == tg_id).one()


@cache.cachable(cache_name="get_user_language", params="tg_id")
def get_user_language(*, tg_id: int) -> str:
    """
    Get user language by tg id
    :param tg_id: the user id
    :return: str
    """

    with get_session() as session:
        return session.query(User.lang).filter(User.tg_id == tg_id).scalar()


# group


def is_group_exists(*, group_id: int) -> bool:
    """Check if group exists or not"""

    with get_session() as session:
        return session.query(exists().where(Group.group_id == group_id)).scalar()  # noqa


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

    _logger.debug(f"Create group: {group_id=}, {name=}, {username=}, {added_by_id=}")

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

    _logger.debug(f"Update group: {group_id=}, {kwargs=}")
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
        return session.query(func.count(User.id)).filter(User.active == True).scalar()  # noqa


def get_users_business_count() -> int:
    """Get all business users count"""

    with get_session() as session:
        return (
            session.query(func.count(User.id)).filter(User.business_id != None).scalar()  # noqa
        )  # noqa


def get_all_users_active() -> list[User]:
    """Get all active users"""

    with get_session() as session:
        return session.query(User).filter(User.active == True).all()  # noqa


def get_all_groups_count() -> int:
    """Get all groups count"""

    with get_session() as session:
        return session.query(func.count(Group.id)).scalar()


def get_groups_count_active() -> int:
    """Get all active groups count"""

    with get_session() as session:
        return session.query(func.count(Group.id)).filter(Group.active == True).scalar()  # noqa


def get_all_groups_active() -> list[Group]:
    """Get all active groups"""

    with get_session() as session:
        return session.query(Group).filter(Group.active == True).all()  # noqa


# message_sent


def create_message_sent(*, sent_id: str, chat_id: int, message_id: int) -> MessageSent:
    """Create message sent
    :param sent_id: the sent id
    :param chat_id: the chat id
    :param message_id: the message id
    :return: :class:`MessageSent`
    """

    _logger.debug(f"Create message sent: {sent_id=}, {chat_id=}, {message_id=}")

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
        return session.query(exists().where(MessageSent.sent_id == sent_id)).scalar()  # noqa


def create_stats(*, type_stats: StatsType, lang: str):
    """Create stats"""

    with get_session() as session:
        stats = Stats(
            type=type_stats.value,
            lang=lang,
            created_at=datetime.datetime.now(),
        )
        session.add(stats)
        session.commit()
