import logging
import threading

from db import repository, tables

_logger = logging.getLogger(__name__)


def create_stats(type_stats: tables.StatsType, lang: str):
    """Create stats"""

    schedule_tread = threading.Thread(
        target=repository.create_stats,
        kwargs=dict(type_stats=type_stats, lang=lang),
        daemon=True,
    )
    schedule_tread.start()
