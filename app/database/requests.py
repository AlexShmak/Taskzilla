"""This file contains all database requests for the bot"""

from app.database.models import User, Project, Task, async_session

from sqlalchemy import BigInteger, select, update, delete


async def set_user(tg_id: int):
    """
    Asynchronously sets a user in the database.

    Args:
        tg_id (int): The Telegram ID of the user.
    """
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def add_project(user_id: BigInteger, name: str) -> None:
    """
    Asynchronously adds a project to the database.

    Args:
        user_id (BigInteger): The TG ID of the user who created the project.
        name (str): The name of the project.
    """
    async with async_session() as session:
        project = await session.scalar(
            select(Project).where(Project.name == name, Project.user_id == user_id)
        )

        if not project:
            session.add(Project(name=name, user_id=user_id))
            await session.commit()


async def add_task(project_id: int, name: str, user_id: BigInteger) -> None:
    """
    Asynchronously adds a task to the database.

    Args:
        project_id (int): The ID of the project that the task belongs to.
        name (str): The name of the task.
    """
    async with async_session() as session:
        task = await session.scalar(
            select(Task).where(
                Task.name == name,
                Task.project_id == project_id,
                Task.user_id == user_id,
            )
        )

        if not task:
            session.add(Task(name=name, project_id=project_id, user_id=user_id))
            await session.commit()


async def get_projects(user_id):
    """
    Asynchronously retrieves all projects associated with the given user ID.

    :param user_id: The ID of the user for whom to retrieve the projects.
    :type user_id: int
    :return: A list of Project objects associated with the user ID.
    :rtype: List[Project]
    """
    async with async_session() as session:
        return await session.scalars(select(Project).where(Project.user_id == user_id))


async def get_project_tasks(project_id, user_id):
    """
    Asynchronously retrieves all tasks associated with the given project ID and user ID.

    :param project_id: The ID of the project for which to retrieve the tasks.
    :type project_id: int
    :param user_id: The ID of the user for whom to retrieve the tasks.
    :type user_id: int
    :return: A list of Task objects associated with the project ID and user ID.
    :rtype: List[Task]
    """
    async with async_session() as session:
        return await session.scalars(
            select(Task).where(Task.project_id == project_id, Task.user_id == user_id)
        )
