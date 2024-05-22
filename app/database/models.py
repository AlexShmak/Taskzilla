"""This file contains all database models for the bot"""

from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker

engine = create_async_engine(
    url="sqlite+aiosqlite:///app/database/db.sqlite3", echo=True
)

async_session = async_sessionmaker(engine)


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


class Project(Base):
    """
    Represents a project in the database.

    Attributes:
        id (int): A unique identifier for the project.
        name (str): The name of the project.
        user_id (BigInteger): The TG ID of the user who created the project.
    """

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    user_id: Mapped[BigInteger] = mapped_column(ForeignKey("users.tg_id"))


class Task(Base):
    """
    Represents a task in the database.

    Attributes:
        id (int): Unique identifier for the task.
        name (str): Name of the task.
        project_id (int): ID of the project that the task belongs to.
        user_id (BigInteger): TG ID of the user who created the task.
    """

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    user_id: Mapped[BigInteger] = mapped_column(ForeignKey("users.tg_id"))


async def async_main():
    """
    Asynchronous function that creates all tables in the database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
