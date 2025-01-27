# This file contains the database tables and their relationships

from __future__ import annotations

import asyncio
import logging
import datetime
from contextlib import asynccontextmanager
from enum import Enum

from sqlalchemy import String, ForeignKey
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    relationship,
)


_logger = logging.getLogger(__name__)


engine = create_async_engine(
    url="sqlite+aiosqlite:///bot_db.sqlite",
)

Session = async_sessionmaker(bind=engine, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncSession:
    """Get async session"""
    async with Session() as session:
        yield session


class StatsType(Enum):
    """Type of stats"""

    BUTTON_SHARE_CHAT = "button_share_chat"
    FORWARD_MESSAGE = "forward_message"
    REPLY_TO_ANOTHER_CHAT = "reply_to_another_chat"
    SEARCH_USERNAME = "search_username"
    ID_IN_GROUP = "id_in_group"
    SEARCH_INLINE = "search_inline"
    VIA_BOT = "via_bot"
    CONTACT = "contact"
    STORY = "story"
    BUSINESS_ID = "business_id"
    BUSINESS_SETTINGS = "business_settings"
    ME = "me"
    LINK = "link"
    ASK_INLINE_QUERY = "ask_inline_query"


class BaseTable(DeclarativeBase):
    pass


class User(BaseTable):
    """User details"""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(String(32))
    username: Mapped[str | None] = mapped_column(String(32))
    business_id: Mapped[str | None] = mapped_column(String(32))
    language_code: Mapped[str | None] = mapped_column(String(5))
    lang: Mapped[str | None] = mapped_column(String(5))  # lang in the bot

    created_at: Mapped[datetime.datetime]
    created_by: Mapped[str | None] = mapped_column(nullable=True)
    # updated_at: Mapped[datetime.datetime] = mapped_column(
    #     default=datetime.datetime.now, onupdate=datetime.datetime.now
    # )

    active: Mapped[bool] = mapped_column(default=True)
    admin: Mapped[bool] = mapped_column(default=False)
    groups: Mapped[list[Group]] = relationship(back_populates="added_by", lazy="joined")


class Group(BaseTable):
    """Group details"""

    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(String(32))
    username: Mapped[str | None] = mapped_column(String(32))
    created_at: Mapped[datetime.datetime]
    active: Mapped[bool] = mapped_column(default=True)
    added_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id"), nullable=True
    )
    added_by: Mapped[User | None] = relationship("User", back_populates="groups")


class MessageSent(BaseTable):
    """Sent message details"""

    __tablename__ = "message_sent"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sent_id: Mapped[str] = mapped_column(String(20))
    message_id: Mapped[int]
    chat_id: Mapped[int]
    sent_at: Mapped[datetime.datetime]


class Stats(BaseTable):
    """Stats details"""

    __tablename__ = "stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[StatsType] = mapped_column(String(32))
    lang: Mapped[str | None] = mapped_column(String(5))

    created_at: Mapped[datetime.datetime]


async def create_tables(engine: AsyncEngine):
    """Create all tables defined in the Base metadata."""
    async with engine.begin() as conn:
        await conn.run_sync(BaseTable.metadata.create_all)


loop = asyncio.get_event_loop()
loop.run_until_complete(create_tables(engine))
