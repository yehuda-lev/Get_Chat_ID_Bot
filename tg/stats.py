import logging
import datetime

from pyrogram import Client, filters, types

from db import repository


_logger = logging.getLogger(__name__)


async def stats_of_the_bot(
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None,
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


async def data_stats_of_the_bot(
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None,
    language_code: str | None = None,
) -> str:
    """
    Get the data stats of the bot
    """

    stats_data = {}
    top_stats_data: dict[str, list[tuple[str, int]]] = {}
    for type_stats in repository.StatsType:
        stats = await repository.get_stats_count(
            type_stats=type_stats,
            language_code=language_code,
            start_date=start_date,
            end_date=end_date,
        )
        stats_data[type_stats.name] = stats

        if language_code is None:
            top_stats = await repository.get_stats_top_langs(
                type_stats=type_stats,
                start_date=start_date,
                end_date=end_date,
            )
            top_stats_data[type_stats.name] = top_stats

    text = "**סטטיסטיקות על המידע של הבוט**\n"
    for stats, count in stats_data.items():
        text += f"**{stats}:** {count}\n"

    if top_stats_data:
        text += "\n**כמות השפות המובילות:**\n"
        for stats, value in top_stats_data.items():
            text += f"**{stats}:**\n"
            for lang, count in value:
                text += f"    {lang}: {count}\n"

    return text
