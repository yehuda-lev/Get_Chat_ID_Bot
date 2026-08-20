from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import Enum

from db import repository
from db.tables import StatsType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class DashboardSection(str, Enum):
    OVERVIEW = "overview"
    SOURCES = "sources"
    TIME = "time"
    LANGUAGES = "languages"
    INSIGHTS = "insights"


class DashboardPeriod(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    ALL = "all"


class DashboardCallbackAction(str, Enum):
    VIEW = "view"
    PERIOD = "period"
    CYCLE = "cycle"
    REFRESH = "refresh"
    EXPORT = "export"


@dataclass(frozen=True)
class DashboardCallbackData:
    action: DashboardCallbackAction
    section: DashboardSection
    period: DashboardPeriod
    step: int = 0


@dataclass(frozen=True)
class DashboardButton:
    text: str
    callback_data: str | None = None


@dataclass(frozen=True)
class DashboardMarkup:
    inline_keyboard: list[list[DashboardButton]]


@dataclass(frozen=True)
class DashboardPage:
    section: DashboardSection
    period: DashboardPeriod
    headline: str
    metrics: list[tuple[str, str]]
    insights: list[str]


SECTION_ORDER = [
    DashboardSection.OVERVIEW,
    DashboardSection.SOURCES,
    DashboardSection.TIME,
    DashboardSection.LANGUAGES,
    DashboardSection.INSIGHTS,
]

PERIOD_LABELS = {
    DashboardPeriod.DAY: "24 שעות אחרונות",
    DashboardPeriod.WEEK: "7 ימים אחרונים",
    DashboardPeriod.MONTH: "30 ימים אחרונים",
    DashboardPeriod.ALL: "כל הזמן",
}

SECTION_LABELS = {
    DashboardSection.OVERVIEW: "סקירה כללית",
    DashboardSection.SOURCES: "מקורות",
    DashboardSection.TIME: "זמן",
    DashboardSection.LANGUAGES: "שפות",
    DashboardSection.INSIGHTS: "תובנות",
}


def cycle_dashboard_section(section: DashboardSection, step: int) -> DashboardSection:
    index = SECTION_ORDER.index(section)
    return SECTION_ORDER[(index + step) % len(SECTION_ORDER)]


def format_change(current: int, previous: int) -> str:
    if previous == 0:
        return "0%" if current == 0 else "+100%"
    delta = round(((current - previous) / previous) * 100)
    sign = "+" if delta > 0 else ""
    return f"{sign}{delta}%"


def build_sparkline(values: list[int]) -> str:
    if not values:
        return ""
    if len(set(values)) == 1:
        return "▁" * len(values)

    buckets = "▁▂▃▄▅▆▇█"
    minimum = min(values)
    maximum = max(values)
    spread = maximum - minimum

    if spread == 0:
        return "▁" * len(values)

    sparkline = []
    for value in values:
        normalized = (value - minimum) / spread
        index = int(normalized * (len(buckets) - 1))
        sparkline.append(buckets[index])
    return "".join(sparkline)


def build_dashboard_callback_data(
    *,
    action: DashboardCallbackAction,
    section: DashboardSection,
    period: DashboardPeriod,
    step: int = 0,
) -> str:
    if action == DashboardCallbackAction.CYCLE:
        return f"stats:{action.value}:{step}:{section.value}:{period.value}"
    if action == DashboardCallbackAction.PERIOD:
        return f"stats:{action.value}:{period.value}:{section.value}"
    return f"stats:{action.value}:{section.value}:{period.value}"


def build_dashboard_keyboard(
    *,
    section: DashboardSection,
    period: DashboardPeriod,
) -> InlineKeyboardMarkup:
    period_buttons = [
        InlineKeyboardButton(
            text="24 שעות",
            callback_data=build_dashboard_callback_data(
                action=DashboardCallbackAction.PERIOD,
                section=section,
                period=DashboardPeriod.DAY,
            ),
        ),
        InlineKeyboardButton(
            text="7 ימים",
            callback_data=build_dashboard_callback_data(
                action=DashboardCallbackAction.PERIOD,
                section=section,
                period=DashboardPeriod.WEEK,
            ),
        ),
        InlineKeyboardButton(
            text="30 ימים",
            callback_data=build_dashboard_callback_data(
                action=DashboardCallbackAction.PERIOD,
                section=section,
                period=DashboardPeriod.MONTH,
            ),
        ),
        InlineKeyboardButton(
            text="הכל",
            callback_data=build_dashboard_callback_data(
                action=DashboardCallbackAction.PERIOD,
                section=section,
                period=DashboardPeriod.ALL,
            ),
        ),
    ]

    section_buttons = [
        InlineKeyboardButton(
            text="סקירה",
            callback_data=build_dashboard_callback_data(
                action=DashboardCallbackAction.VIEW,
                section=DashboardSection.OVERVIEW,
                period=period,
            ),
        ),
        InlineKeyboardButton(
            text="מקורות",
            callback_data=build_dashboard_callback_data(
                action=DashboardCallbackAction.VIEW,
                section=DashboardSection.SOURCES,
                period=period,
            ),
        ),
        InlineKeyboardButton(
            text="זמן",
            callback_data=build_dashboard_callback_data(
                action=DashboardCallbackAction.VIEW,
                section=DashboardSection.TIME,
                period=period,
            ),
        ),
    ]

    second_section_buttons = [
        InlineKeyboardButton(
            text="שפות",
            callback_data=build_dashboard_callback_data(
                action=DashboardCallbackAction.VIEW,
                section=DashboardSection.LANGUAGES,
                period=period,
            ),
        ),
        InlineKeyboardButton(
            text="תובנות",
            callback_data=build_dashboard_callback_data(
                action=DashboardCallbackAction.VIEW,
                section=DashboardSection.INSIGHTS,
                period=period,
            ),
        ),
        InlineKeyboardButton(
            text="רענון",
            callback_data=build_dashboard_callback_data(
                action=DashboardCallbackAction.REFRESH,
                section=section,
                period=period,
            ),
        ),
    ]

    navigation_buttons = [
        InlineKeyboardButton(
            text="◀",
            callback_data=build_dashboard_callback_data(
                action=DashboardCallbackAction.CYCLE,
                section=section,
                period=period,
                step=-1,
            ),
        ),
        InlineKeyboardButton(
            text="▶",
            callback_data=build_dashboard_callback_data(
                action=DashboardCallbackAction.CYCLE,
                section=section,
                period=period,
                step=1,
            ),
        ),
    ]

    return InlineKeyboardMarkup(
        [
            period_buttons,
            section_buttons,
            second_section_buttons,
            navigation_buttons,
        ]
    )


def get_period_bounds(
    period: DashboardPeriod,
    *,
    now: datetime.datetime | None = None,
) -> tuple[datetime.datetime | None, datetime.datetime | None]:
    now = now or datetime.datetime.now()
    if period == DashboardPeriod.ALL:
        return None, None

    delta = {
        DashboardPeriod.DAY: datetime.timedelta(days=1),
        DashboardPeriod.WEEK: datetime.timedelta(days=7),
        DashboardPeriod.MONTH: datetime.timedelta(days=30),
    }[period]
    end = now
    start = end - delta
    return start, end


def get_previous_bounds(
    start: datetime.datetime | None,
    end: datetime.datetime | None,
) -> tuple[datetime.datetime | None, datetime.datetime | None]:
    if start is None or end is None:
        return None, None
    length = end - start
    previous_end = start
    previous_start = previous_end - length
    return previous_start, previous_end


def _label_stat_type(stat_type: str) -> str:
    labels = {
        StatsType.BUTTON_SHARE_CHAT.value: "שיתוף צ'אט",
        StatsType.FORWARD_MESSAGE.value: "Forward",
        StatsType.REPLY_TO_ANOTHER_CHAT.value: "Reply לצ'אט אחר",
        StatsType.SEARCH_USERNAME.value: "חיפוש לפי username",
        StatsType.ID_IN_GROUP.value: "ID בקבוצה",
        StatsType.ID_BY_GUEST_MODE.value: "Guest mode",
        StatsType.ID_FOR_EPHEMERAL_COMMAND.value: "Ephemeral command",
        StatsType.SEARCH_INLINE.value: "Inline search",
        StatsType.VIA_BOT.value: "Via bot",
        StatsType.CONTACT.value: "Contact",
        StatsType.STORY.value: "Story",
        StatsType.BUSINESS_ID.value: "Business ID",
        StatsType.BUSINESS_SETTINGS.value: "Business settings",
        StatsType.ME.value: "Me",
        StatsType.LINK.value: "Link",
        StatsType.ASK_INLINE_QUERY.value: "Ask inline query",
    }
    return labels.get(stat_type, stat_type.replace("_", " ").title())


def _format_count(value: int) -> str:
    return f"{value:,}".replace(",", ",")


def _format_language(lang: str | None) -> str:
    if not lang:
        return "לא ידוע"
    if lang == "he":
        return "עברית"
    if lang == "en":
        return "אנגלית"
    if lang == "ar":
        return "ערבית"
    if lang == "ru":
        return "רוסית"
    if lang == "zh-hans":
        return "סינית"
    return lang


async def build_dashboard_page(
    *,
    section: DashboardSection,
    period: DashboardPeriod,
    repo=repository,
    now: datetime.datetime | None = None,
) -> DashboardPage:
    start, end = get_period_bounds(period, now=now)
    previous_start, previous_end = get_previous_bounds(start, end)

    stats_by_type = await repo.get_stats_counts_by_type(
        start_date=start, end_date=end
    )
    stats_total = sum(count for _, count in stats_by_type)
    previous_stats_total = 0
    if previous_start and previous_end:
        previous_stats_by_type = await repo.get_stats_counts_by_type(
            start_date=previous_start,
            end_date=previous_end,
        )
        previous_stats_total = sum(count for _, count in previous_stats_by_type)

    top_sources = sorted(stats_by_type, key=lambda item: item[1], reverse=True)[:5]
    stats_by_lang = await repo.get_stats_counts_by_lang(
        start_date=start, end_date=end
    )
    top_langs = sorted(stats_by_lang, key=lambda item: item[1], reverse=True)[:5]
    stats_by_day = await repo.get_stats_counts_by_day(start_date=start, end_date=end)

    users_total = await repo.get_users_count()
    users_active = await repo.get_users_count(
        active=True,
        last_active_start=start,
        last_active_end=end,
    )
    users_new = await repo.get_users_count(
        created_start=start,
        created_end=end,
    )
    groups_total = await repo.get_groups_count()
    groups_active = await repo.get_groups_count(active=True)
    groups_new = await repo.get_groups_count(
        created_start=start,
        created_end=end,
    )

    if section == DashboardSection.OVERVIEW:
        headline = "תמונת מצב קצרה של הבוט"
        metrics = [
            ("סך פעולות", _format_count(stats_total)),
            ("שינוי מול תקופה קודמת", format_change(stats_total, previous_stats_total)),
            ("משתמשים פעילים", _format_count(users_active)),
            ("משתמשים חדשים", _format_count(users_new)),
            ("קבוצות פעילות", _format_count(groups_active)),
            ("קבוצות חדשות", _format_count(groups_new)),
        ]
        insights = []
        if top_sources:
            insights.append(f"פעולת השיא היא {_label_stat_type(top_sources[0][0])}")
        if top_langs:
            insights.append(f"השפה המובילה היא {_format_language(top_langs[0][0])}")

    elif section == DashboardSection.SOURCES:
        headline = "חלוקת השימוש לפי מקור"
        metrics = [
            (f"{_label_stat_type(stat_type)}", _format_count(count))
            for stat_type, count in top_sources
        ]
        insights = [
            f"{_label_stat_type(stat_type)} מוביל עם {_format_count(count)} אירועים"
            for stat_type, count in top_sources[:2]
        ]

    elif section == DashboardSection.TIME:
        headline = "מגמה לפי ימים"
        sparkline = build_sparkline([count for _, count in stats_by_day])
        metrics = [
            ("רצף פעילות", sparkline or "אין עדיין נתונים"),
        ]
        metrics.extend(
            (day, _format_count(count))
            for day, count in stats_by_day[-7:]
        )
        insights = []
        if stats_by_day:
            insights.append(
                f"היום החזק ביותר במקטע הוא {_format_count(max(count for _, count in stats_by_day))} אירועים"
            )

    elif section == DashboardSection.LANGUAGES:
        headline = "השפות הבולטות בתקופה"
        metrics = [
            (_format_language(lang), _format_count(count))
            for lang, count in top_langs
        ]
        insights = [
            f"{_format_language(lang)} אחראית ל-{_format_count(count)} אירועים"
            for lang, count in top_langs[:2]
        ]

    else:
        headline = "תובנות שמסכמות את הפעילות"
        metrics = [
            ("סך פעולות", _format_count(stats_total)),
            ("משתמשים חדשים", _format_count(users_new)),
            ("משתמשים פעילים", _format_count(users_active)),
            ("קבוצות חדשות", _format_count(groups_new)),
            ("קבוצות פעילות", _format_count(groups_active)),
            ("סה\"כ משתמשים", _format_count(users_total)),
            ("סה\"כ קבוצות", _format_count(groups_total)),
        ]
        insights = []
        if stats_total:
            insights.append(f"הממוצע היומי הוא {_format_count(round(stats_total / max(len(stats_by_day), 1)))}")
        if top_sources:
            insights.append(f"המקור המוביל הוא {_label_stat_type(top_sources[0][0])}")
        if top_langs:
            insights.append(f"השפה המובילה היא {_format_language(top_langs[0][0])}")

    return DashboardPage(
        section=section,
        period=period,
        headline=headline,
        metrics=metrics,
        insights=insights,
    )


def render_dashboard_page(page: DashboardPage) -> str:
    return format_dashboard_message(
        section=page.section,
        period=page.period,
        headline=page.headline,
        metrics=page.metrics,
        insights=page.insights,
    )


def parse_dashboard_callback_data(data: str) -> DashboardCallbackData:
    prefix, action_value, *payload = data.split(":")
    if prefix != "stats":
        raise ValueError(f"Unsupported callback prefix: {prefix}")

    action = DashboardCallbackAction(action_value)
    if action == DashboardCallbackAction.CYCLE:
        step = int(payload[0])
        section = DashboardSection(payload[1])
        period = DashboardPeriod(payload[2])
        return DashboardCallbackData(
            action=action,
            section=section,
            period=period,
            step=step,
        )
    if action == DashboardCallbackAction.PERIOD:
        period = DashboardPeriod(payload[0])
        section = DashboardSection(payload[1])
        return DashboardCallbackData(
            action=action,
            section=section,
            period=period,
        )

    section = DashboardSection(payload[0])
    period = DashboardPeriod(payload[1])
    return DashboardCallbackData(
        action=action,
        section=section,
        period=period,
    )


def format_dashboard_message(
    *,
    section: DashboardSection,
    period: DashboardPeriod,
    headline: str,
    metrics: list[tuple[str, str]],
    insights: list[str],
) -> str:
    lines = [SECTION_LABELS[section], PERIOD_LABELS[period], headline]
    for label, value in metrics:
        lines.append(f"{label}: {value}")
    if insights:
        lines.append("")
        lines.append("תובנות")
        lines.extend(f"- {item}" for item in insights)
    return "\n".join(lines)
