import logging
import datetime

from pyrogram import Client, filters, types

from db import repository


_logger = logging.getLogger(__name__)


async def ask_stats_time(_: Client, message: types.Message):
    """
    Ask the user for the stats time
    """
    dict_buttons_data = {
        "ask_stats:all": "סטטיסטיקות על כל הזמן",
        "ask_stats:day": "סטטיסטיקות על היום",
        "ask_stats:week": "סטטיסטיקות על השבוע",
        "ask_stats:month": "סטטיסטיקות על החודש",
        "ask_stats:two_months": "סטטיסטיקות על חודשיים",
    }

    buttons = [
        [types.InlineKeyboardButton(text=text, callback_data=callback_data)]
        for callback_data, text in dict_buttons_data.items()
    ]

    keyboard = types.InlineKeyboardMarkup(buttons)

    await message.reply_text(
        "בחר את הסטטיסטיקות שתרצה לקבל",
        reply_markup=keyboard,
    )


async def ask_stats_language(_: Client, query: types.CallbackQuery):
    """
    Ask the user for the stats language
    """

    time = query.data.split(":")[1]

    dict_buttons_data = {
        f"get_stats:{time}:all": "כל השפות",
        f"get_stats:{time}:en": "אנגלית",
        f"get_stats:{time}:he": "עברית",
        f"get_stats:{time}:ru": "רוסית",
        f"get_stats:{time}:ar": "ערבית",
        f"get_stats:{time}:zh-hans": "סינית",
        f"get_stats:{time}:id": "אינדונזית",
        f"get_stats:{time}:uz": "אוזבקית",
        f"get_stats:{time}:tr": "טורקית",
        f"get_stats:{time}:pt-br": "פורטוגזית",
        f"get_stats:{time}:uk": "אוקראינית",
        f"get_stats:{time}:es": "ספרדית",
        f"get_stats:{time}:fr": "צרפתית",
        f"get_stats:{time}:de": "גרמנית",
        f"get_stats:{time}:fa": "פרסית",
        f"get_stats:{time}:it": "איטלקית",
        f"get_stats:{time}:pl": "פולנית",
        f"get_stats:{time}:vi": "וייטנאמית",
    }

    buttons = [
        [types.InlineKeyboardButton(text=text, callback_data=callback_data)]
        for callback_data, text in dict_buttons_data.items()
    ]

    keyboard = types.InlineKeyboardMarkup(buttons)

    await query.message.reply(
        "בחר את השפה שתרצה לקבל את הסטטיסטיקות",
        reply_markup=keyboard,
    )


async def get_stats(_: Client, query: types.CallbackQuery):
    """
    Get the stats
    """

    time, language_code = query.data.split(":")[1:]
    language_code = language_code if language_code != "all" else None
    statr_date, end_date = None, None

    if time == "all":
        start_date = None
        end_date = None
    else:
        start_date = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        if time == "day":
            end_date = start_date + datetime.timedelta(days=1)
        elif time == "week":
            end_date = start_date + datetime.timedelta(days=7)
        elif time == "month":
            end_date = start_date + datetime.timedelta(days=30)
        elif time == "two_months":
            end_date = start_date + datetime.timedelta(days=60)

    text_stats_bot = await stats_of_the_bot(start_date, end_date, language_code)
    text_data_stats_bot = await data_stats_of_the_bot(
        start_date, end_date, language_code
    )

    text = (
        f"**סטטיסטיקות על הבוט**\n\n"
        f"סטטיסטיקות לפי תאריכים: {start_date} - {end_date}\n\n"
        f"סטטיסטיקות לפי שפה: {language_code}\n\n"
        f"{text_stats_bot}\n\n{text_data_stats_bot}"
    )

    await query.message.reply(text)


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
