# This file contains the database tables and their relationships

from __future__ import annotations
import logging
import datetime
from contextlib import contextmanager
from sqlalchemy import String, create_engine, ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    sessionmaker,
    relationship,
)


_logger = logging.getLogger(__name__)


engine = create_engine(
    url="sqlite:///bot_db.sqlite",
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
)

Session = sessionmaker(bind=engine)


@contextmanager
def get_session() -> Session:
    """Get session"""
    new_session = Session()
    try:
        yield new_session
    finally:
        new_session.close()


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
    created_at: Mapped[datetime.datetime]
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
    added_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    added_by: Mapped[User] = relationship("User", back_populates="groups")


class MessageSent(BaseTable):
    """Sent message details"""

    __tablename__ = "message_sent"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sent_id: Mapped[str] = mapped_column(String(20))
    message_id: Mapped[int]
    chat_id: Mapped[int]
    sent_at: Mapped[datetime.datetime]


BaseTable.metadata.create_all(engine)
