import asyncio

from tg.stats_dashboard import (
    DashboardCallbackAction,
    DashboardPeriod,
    DashboardSection,
    build_dashboard_keyboard,
    build_dashboard_callback_data,
    build_dashboard_page,
    cycle_dashboard_section,
    format_change,
    format_dashboard_message,
    build_sparkline,
    parse_dashboard_callback_data,
    render_dashboard_page,
)


def test_cycle_dashboard_section_wraps_in_both_directions():
    assert (
        cycle_dashboard_section(DashboardSection.OVERVIEW, 1)
        == DashboardSection.SOURCES
    )
    assert (
        cycle_dashboard_section(DashboardSection.OVERVIEW, -1)
        == DashboardSection.INSIGHTS
    )


def test_format_dashboard_message_includes_requested_content():
    text = format_dashboard_message(
        section=DashboardSection.OVERVIEW,
        period=DashboardPeriod.WEEK,
        headline="פעילות השבוע עלתה ב-18%",
        metrics=[
            ("סך פעולות", "12,480"),
            ("משתמשים פעילים", "1,240"),
        ],
        insights=["forward הוא מקור השימוש המוביל"],
    )

    assert "סקירה כללית" in text
    assert "7 ימים אחרונים" in text
    assert "פעילות השבוע עלתה ב-18%" in text
    assert "סך פעולות: 12,480" in text
    assert "forward הוא מקור השימוש המוביל" in text


def test_dashboard_callback_round_trip():
    callback = build_dashboard_callback_data(
        action=DashboardCallbackAction.VIEW,
        section=DashboardSection.SOURCES,
        period=DashboardPeriod.MONTH,
    )

    parsed = parse_dashboard_callback_data(callback)

    assert parsed.action == DashboardCallbackAction.VIEW
    assert parsed.section == DashboardSection.SOURCES
    assert parsed.period == DashboardPeriod.MONTH


def test_format_change_and_sparkline_show_trend():
    assert format_change(12, 10) == "+20%"
    assert format_change(0, 0) == "0%"
    assert build_sparkline([0, 2, 5, 10]) == "▁▂▄█"


def test_build_dashboard_keyboard_exposes_navigation_callbacks():
    markup = build_dashboard_keyboard(
        section=DashboardSection.OVERVIEW,
        period=DashboardPeriod.WEEK,
    )

    callback_data = {
        button.callback_data
        for row in markup.inline_keyboard
        for button in row
        if button.callback_data
    }

    assert "stats:view:sources:week" in callback_data
    assert "stats:period:day:overview" in callback_data
    assert "stats:cycle:1:overview:week" in callback_data


def test_build_dashboard_page_uses_repository_snapshot():
    class FakeRepo:
        async def get_stats_counts_by_type(self, **_kwargs):
            return [("forward_message", 12), ("me", 3)]

        async def get_stats_counts_by_lang(self, **_kwargs):
            return [("he", 10), ("en", 5)]

        async def get_stats_counts_by_day(self, **_kwargs):
            return [("2026-08-18", 4), ("2026-08-19", 6)]

        async def get_users_count(self, **_kwargs):
            if _kwargs.get("active"):
                return 8
            if _kwargs.get("created_start") is not None:
                return 2
            return 14

        async def get_groups_count(self, **_kwargs):
            if _kwargs.get("active"):
                return 4
            if _kwargs.get("created_start") is not None:
                return 1
            return 6

    page = asyncio.run(
        build_dashboard_page(
            section=DashboardSection.OVERVIEW,
            period=DashboardPeriod.WEEK,
            repo=FakeRepo(),
        )
    )

    assert page.headline == "תמונת מצב קצרה של הבוט"
    assert page.metrics[0] == ("סך פעולות", "15")
    assert any("פעולת השיא" in item for item in page.insights)
    text = render_dashboard_page(page)
    assert "סקירה כללית" in text
    assert "סך פעולות: 15" in text
