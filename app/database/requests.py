"""This file contains all database requests for the bot"""

from app.database.models import User, Project, Task, async_session, TaskStatus

from sqlalchemy import BigInteger, select, update, delete


async def add_user(tg_id: int):
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


async def get_project_name(project_id, user_id):
    """
    Asynchronously retrieves the name of a project
        based on its ID and the ID of the user who owns it.

    :param project_id: The ID of the project to retrieve the name for.
    :type project_id: int
    :param user_id: The ID of the user who owns the project.
    :type user_id: int
    :return: The name of the project if it exists, None otherwise.
    :rtype: str or None
    """
    async with async_session() as session:
        project = await session.scalar(
            select(Project).where(Project.id == project_id, Project.user_id == user_id)
        )

        return project.name


async def get_task_name(task_id, project_id, user_id):
    """
    Asynchronously retrieves the name of a task based on its ID, project ID, and user ID.

    :param task_id: The ID of the task to retrieve the name for.
    :type task_id: int
    :param project_id: The ID of the project the task belongs to.
    :type project_id: int
    :param user_id: The ID of the user who owns the task.
    :type user_id: int
    :return: The name of the task if it exists, None otherwise.
    :rtype: str or None
    """
    async with async_session() as session:
        task = await session.scalar(
            select(Task).where(
                Task.id == task_id,
                Task.project_id == project_id,
                Task.user_id == user_id,
            )
        )
        return task.name


async def get_general_project_id(user_id):
    """
    Asynchronously retrieves the ID of the "General" project associated with the given user ID.

    Args:
        user_id (int): The ID of the user.

    Returns:
        int or None: The ID of the "General" project if it exists, None otherwise.
    """
    async with async_session() as session:
        project = await session.scalar(
            select(Project).where(Project.user_id == user_id, Project.name == "General")
        )

        return project.id


async def get_task_id(task_name, project_id, user_id):
    """
    Asynchronously retrieves the ID of a task based on its name, project ID, and user ID.

    :param task_name: The name of the task to retrieve the ID for.
    :type task_name: str
    :param project_id: The ID of the project the task belongs to.
    :type project_id: int
    :param user_id: The ID of the user who owns the task.
    :type user_id: int
    :return: The ID of the task if it exists, None otherwise.
    :rtype: int or None
    """
    async with async_session() as session:
        task = await session.scalar(
            select(Task).where(
                Task.name == task_name,
                Task.project_id == project_id,
                Task.user_id == user_id,
            )
        )

        return task.id


async def project_is_general(project_id, user_id):
    """
    Asynchronously checks if a project is the "General" project for a given user.

    Args:
        project_id (int): The ID of the project to check.
        user_id (int): The ID of the user.

    Returns:
        bool: True if the project is the "General" project for the user, False otherwise.
    """
    async with async_session() as session:
        project = await session.scalar(
            select(Project).where(
                (Project.id == project_id)
                & (Project.user_id == user_id)
                & (Project.name == "General")
            )
        )

        return bool(project)


async def get_task_status(task_id, project_id, user_id):
    """
    Asynchronously retrieves the status of a task given its ID, project ID, and user ID.

    :param task_id: The ID of the task to retrieve the status for.
    :type task_id: int
    :param project_id: The ID of the project the task belongs to.
    :type project_id: int
    :param user_id: The ID of the user who owns the task.
    :type user_id: int
    :return: The status of the task.
    :rtype: str
    """
    async with async_session() as session:
        task = await session.scalar(
            select(Task).where(
                Task.id == task_id,
                Task.project_id == project_id,
                Task.user_id == user_id,
            )
        )
        return task.status


async def get_task_emoji(task_id, project_id, user_id):
    """
    Asynchronously retrieves the emoji of a task given its ID, project ID, and user ID.

    :param task_id: The ID of the task to retrieve the emoji for.
    :type task_id: int
    :param project_id: The ID of the project the task belongs to.
    :type project_id: int
    :param user_id: The ID of the user who owns the task.
    :type user_id: int
    :return: The emoji of the task.
    :rtype: str
    """
    async with async_session() as session:
        task = await session.scalar(
            select(Task).where(
                Task.id == task_id,
                Task.project_id == project_id,
                Task.user_id == user_id,
            )
        )
        return task.emoji


async def change_task_status_to_inprogress(task_id, project_id, user_id, new_status):
    async with async_session() as session:
        await session.execute(
            update(Task)
            .where(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.project_id == project_id,
            )
            .values(
                emoji="🔵",
                status=new_status,
            )
        )
        await session.commit()


async def change_task_status_to_notstarted(task_id, project_id, user_id, new_status):
    async with async_session() as session:
        await session.execute(
            update(Task)
            .where(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.project_id == project_id,
            )
            .values(
                emoji="🟣",
                status=new_status,
            )
        )
        await session.commit()


async def change_task_status_to_completed(task_id, project_id, user_id, new_status):
    async with async_session() as session:
        await session.execute(
            update(Task)
            .where(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.project_id == project_id,
            )
            .values(
                emoji="🟢",
                status=new_status,
            )
        )
        await session.commit()
