import logging
import datetime

from pyrogram import Client, filters, types

from db import repository


_logger = logging.getLogger(__name__)


async def stats_of_the_bot(
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    language_code: str | None = None,
) -> str:
    """
    Get the stats of the bot
    """
    users = await repository.get_users_count(
        language_code=language_code, created_start=start_date, created_end=end_date
    )
    users_active = await repository.get_users_count(
        active=True,
        language_code=language_code,
        created_start=start_date,
        created_end=end_date,
    )
    business = await repository.get_users_count(
        business=True,
        language_code=language_code,
        created_start=start_date,
        created_end=end_date,
    )

    groups = await repository.get_groups_count(
        created_start=start_date, created_end=end_date
    )
    groups_active = await repository.get_groups_count(
        active=True, created_start=start_date, created_end=end_date
    )

    return (
        f"**סטטיסטיקות על הבוט**\n"
        f"**כמות היוזרים המנויים בבוט הם:** \n"
        f"הכל: {users}\n"
        f"פעילים: {users_active}\n"
        f"לא פעילים: {users - users_active}\n"
        f"משתמשי ביזנס {business}\n\n"
        f"**כמות הקבוצות בבוט הם:** \n"
        f"הכל: {groups}\n"
        f"פעילות: {groups_active}\n"
        f"לא פעילות: {groups - groups_active}\n"
    )
