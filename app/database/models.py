"""This file contains all database models for the bot"""

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs


engine = create_async_engine(url="sqlite+aiosqlite:///database/db.sqlite3")


class Base(DeclarativeBase, AsyncAttrs):
    """
    Base class for all database models.
    Contains common attributes and methods for all models.
    """


class User(Base):
    """
    Represents a user in the database.

    Attributes:
        id (int): A unique identifier for the user.
        tg_id (BigInteger): The user's Telegram ID.
        name (str): The user's name.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(25))


class Task(Base):
    """
    Represents a task in the database.

    Attributes:
        id (int): A unique identifier for the task.
        name (str): The task's name.
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
