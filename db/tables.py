# This file contains the database tables and their relationships

from __future__ import annotations

import asyncio
import enum
import logging
import datetime
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from sqlmodel import SQLModel, Field, Relationship


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


class StatsType(enum.Enum):
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


class User(SQLModel, table=True):
    """User details"""

    __tablename__ = "user"

    id: int | None = Field(primary_key=True)
    tg_id: int = Field(unique=True)
    name: str = Field(max_length=32)
    username: str | None = Field(max_length=32)
    business_id: str | None = Field(max_length=32)
    language_code: str | None = Field(max_length=5)
    lang: str | None = Field(max_length=5)  # lang in the bot

    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    created_by: str | None
    # updated_at: datetime.datetime = Field(
    #     default_factory=datetime.datetime.now,
    #     sa_column_kwargs={"onupdate":datetime.datetime.now}
    # )

    active: bool = Field(default=True)
    admin: bool = Field(default=False)
    groups: list[Group] = Relationship(back_populates="added_by")
    feature: Feature | None = Relationship(back_populates="user")


class Feature(SQLModel, table=True):
    """Feature details"""

    __tablename__ = "feature"

    id: int | None = Field(primary_key=True)
    copy_button: bool = Field(default=True)
    multiple_chats: bool = Field(default=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        sa_column_kwargs={"onupdate": datetime.datetime.now},
    )

    user_id: int = Field(foreign_key="user.id", unique=True)
    user: User = Relationship(back_populates="feature")


class Group(SQLModel, table=True):
    """Group details"""

    __tablename__ = "group"

    id: int | None = Field(primary_key=True)
    group_id: int = Field(unique=True)
    name: str = Field(max_length=32)
    username: str | None = Field(max_length=32)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    active: bool = Field(default=True)
    added_by_id: int | None = Field(foreign_key="user.id")
    added_by: User = Relationship(back_populates="groups")


class MessageSent(SQLModel, table=True):
    """Sent message details"""

    __tablename__ = "message_sent"

    id: int | None = Field(default=None, primary_key=True)
    sent_id: str = Field(max_length=20)
    message_id: int
    chat_id: int
    sent_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class Stats(SQLModel, table=True):
    """Stats details"""

    __tablename__ = "stats"

    id: int | None = Field(primary_key=True)
    type: StatsType = Field(
        sa_column_kwargs={"type": enum.Enum}
    )  # TODO change to Enum type!
    lang: str | None = Field(max_length=5)

    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


async def create_tables():
    """Create all tables defined in the Base metadata."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


loop = asyncio.get_event_loop()
loop.run_until_complete(create_tables())
