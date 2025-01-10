import logging
import asyncio

from db import repository, tables

_logger = logging.getLogger(__name__)


def create_stats(type_stats: tables.StatsType, lang: str):
    """Create stats"""

    asyncio.create_task(
        repository.create_stats(type_stats=type_stats, lang=lang),
    )
