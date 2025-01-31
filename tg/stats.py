import logging

from pyrogram import Client, filters, types

from db import repository


async def stats(_: Client, msg: types.Message):  # command /stats
    """
    Get the stats of the bot.
    """
    users = await repository.get_users_count_by_filters()
    users_active = await repository.get_users_count_by_filters(active=True)
    business = await repository.get_users_count_by_filters(business=True)

    groups = await repository.get_groups_count_by_filters()
    groups_active = await repository.get_groups_count_by_filters(active=True)

    text = (
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

    await msg.reply(text=text, quote=True)
