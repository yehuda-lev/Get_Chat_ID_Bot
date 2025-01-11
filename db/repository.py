# this file contains all the database operations

import datetime
import logging
from sqlalchemy import exists, func, select, update

from db.tables import get_session, User, Group, MessageSent, StatsType, Stats
from data import cache_memory


_logger = logging.getLogger(__name__)

cache = cache_memory.cache_memory


# user


async def create_user(
    *,
    tg_id: int,
    name: str,
    username: str = None,
    language_code: str,
    created_by: str | None = None,
    admin: bool = False,
    active: bool = True,
) -> User:
    """
    Create tg user
    :param tg_id: the user id
    :param name: the name of user
    :param username: the username of user
    :param language_code: the language code of user
    :param created_by: the word the user joined the bot (stats)
    :param admin: is admin or not, default is False
    :param active: is active or not, default is True

    :Returns: User
    """

    _logger.debug(f"Create user: {tg_id=}, {name=}, {username=}, {language_code=}")
    # delete cache
    cache.delete("get_user", cache_id=cache.build_cache_id(tg_id=tg_id))

    async with get_session() as session:
        user = User(
            tg_id=tg_id,
            name=name,
            username=username,
            language_code=language_code,
            lang=language_code,
            created_by=created_by,
            admin=admin,
            active=active,
            created_at=datetime.datetime.now(),
        )
        session.add(user)
        await session.commit()
        return user


async def update_user(*, tg_id: int, **kwargs):
    """
    Update user
    :param tg_id: the user id
    :param kwargs: the data to update
    """

    _logger.debug(f"Update user: {tg_id=}, {kwargs=}")
    # delete cache
    cache.delete("get_user", cache_id=cache.build_cache_id(tg_id=tg_id))

    async with get_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(**kwargs))
        await session.commit()


@cache.cachable(cache_name="get_user", params="tg_id")
async def get_user(*, tg_id: int) -> User:
    """
    Retrieve a user by Telegram ID.
    """
    async with get_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


# group


async def create_group(
    *,
    group_id: int,
    name: str,
    username: str | None = None,
    added_by_id: int | None = None,
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
    # delete cache
    cache.delete("get_group", cache_id=cache.build_cache_id(group_id=group_id))

    async with get_session() as session:
        if added_by_id:
            user = await get_user(tg_id=added_by_id)
        else:
            user = None
        group = Group(
            group_id=group_id,
            name=name,
            username=username,
            created_at=datetime.datetime.now(),
            added_by=user,
            active=active,
        )
        session.add(group)
        await session.commit()


async def update_group(*, group_id: int, **kwargs):
    """
    Update group
    :param group_id: the group id
    :param kwargs: the data to update
    """

    _logger.debug(f"Update group: {group_id=}, {kwargs=}")
    # delete cache
    cache.delete("get_group", cache_id=cache.build_cache_id(group_id=group_id))

    async with get_session() as session:
        await session.execute(
            update(Group).where(Group.group_id == group_id).values(**kwargs)
        )
        await session.commit()


@cache.cachable(cache_name="get_group", params="group_id")
async def get_group(*, group_id: int) -> Group:
    """
    Retrieve a group by its ID.
    """
    async with get_session() as session:
        return await session.scalar(select(Group).where(Group.group_id == group_id))


# stats


async def get_all_users_count() -> int:
    """
    Get the total number of users.
    """
    async with get_session() as session:
        return await session.scalar(select(func.count(User.id)))


async def get_users_count_active() -> int:
    """
    Get the total number of active users.
    """
    async with get_session() as session:
        return await session.scalar(
            select(func.count(User.id)).where(User.active == True)  # noqa
        )


async def get_users_business_count() -> int:
    """
    Get the total number of business users.
    """
    async with get_session() as session:
        return await session.scalar(
            select(func.count(User.id)).where(User.business_id != None)  # noqa
        )


async def get_all_users_active() -> list[User]:
    """
    Get all active users.
    """
    async with get_session() as session:
        result = await session.execute(select(User).where(User.active == True))  # noqa
        # TODO not working
        return result.scalars().all()


async def get_all_groups_count() -> int:
    """
    Get the total number of groups.
    """
    async with get_session() as session:
        return await session.scalar(select(func.count(Group.id)))


async def get_groups_count_active() -> int:
    """
    Get the total number of active groups.
    """
    async with get_session() as session:
        return await session.scalar(
            select(func.count(Group.id)).where(Group.active == True)  # noqa
        )


async def get_all_groups_active() -> list[Group]:
    """
    Get all active groups.
    """
    async with get_session() as session:
        result = await session.execute(select(Group).where(Group.active == True))  # noqa
        return result.scalars().all()


# message sent


async def create_message_sent(
    *, sent_id: str, chat_id: int, message_id: int
) -> MessageSent:
    """
    Create a message sent record.
    """
    _logger.debug(f"Create message sent: {sent_id=}, {chat_id=}, {message_id=}")

    async with get_session() as session:
        message_sent = MessageSent(
            sent_id=sent_id,
            chat_id=chat_id,
            message_id=message_id,
            sent_at=datetime.datetime.now(),
        )
        session.add(message_sent)
        await session.commit()
        return message_sent


async def get_messages_sent(*, sent_id: str) -> list[MessageSent]:
    """
    Get messages sent by a specific sent_id.
    """
    async with get_session() as session:
        result = await session.execute(
            select(MessageSent).where(MessageSent.sent_id == sent_id)
        )
        return result.scalars().all()


async def is_message_sent_exists(*, sent_id: str) -> bool:
    """
    Check if a message sent record exists.
    """
    async with get_session() as session:
        result = await session.scalar(
            exists().where(MessageSent.sent_id == sent_id).select()
        )
        return result


async def create_stats(*, type_stats: StatsType, lang: str):
    """
    Create a statistics record.
    """
    async with get_session() as session:
        stats = Stats(
            type=type_stats.value,
            lang=lang,
            created_at=datetime.datetime.now(),
        )
        session.add(stats)
        await session.commit()
