"""This file contains all keyboars for the bot"""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import (
    get_projects,
    get_project_tasks,
    get_general_project_id,
    get_task_emoji,
)


# General keyboard
async def starting_kb(user_id):
    """
    Asynchronously creates an inline keyboard markup with buttons to create a new task,
    a new project, or list general tasks or projects. The callback data for each button is
    dynamically generated using the provided user_id.

    :param user_id: The ID of the user.
    :type user_id: int
    :return: An InlineKeyboardMarkup object with the buttons and callback data.
    :rtype: InlineKeyboardMarkup
    """
    project_id = await get_general_project_id(user_id)
    start_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝Новая задача",
                    callback_data=f"new_task_{project_id}_general",
                ),
                InlineKeyboardButton(
                    text="📚Новый проект", callback_data="new_project_general"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✅Список общих задач", callback_data="list_general_tasks"
                )
            ],
            [
                InlineKeyboardButton(
                    text="☑️Список проектов", callback_data="list_projects"
                )
            ],
        ],
    )
    return start_kb


async def change_task_kb(project_id):
    """
    Asynchronously creates an inline keyboard markup with buttons to rename or delete a task,
    and a back button. The callback data for each button is dynamically generated using the
    provided project_id.

    :param project_id: The ID of the project that the task belongs to.
    :type project_id: int
    :return: An InlineKeyboardMarkup object with the buttons and callback data.
    :rtype: InlineKeyboardMarkup
    """
    change_t_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝Переименовать задачу",
                    callback_data=f"rename_task_{project_id}",
                ),
                InlineKeyboardButton(
                    text="❌Удалить", callback_data=f"delete_task_{project_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙Назад", callback_data=f"list_tasks_{project_id}"
                )
            ],
        ],
        resize_keyboard=False,
    )
    return change_t_kb


change_project_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📝Переименовать проект", callback_data="rename_project"
            ),
            InlineKeyboardButton(text="❌Удалить", callback_data="delete_project"),
        ],
        [InlineKeyboardButton(text="🔙Назад", callback_data="project")],
    ],
)


# Keyboards to interact with tasks
async def manage_task(project_id, task_id, back_callback_data, position):
    """
    Asynchronously creates an inline keyboard markup for managing a task.
    :param project_id: The ID of the project the task belongs to.
    :type project_id: int
    :param task_id: The ID of the task to manage.
    :type task_id: int
    :return: An inline keyboard markup for managing the task.
    :rtype: InlineKeyboardMarkup
    """

    task_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟣Не начата",
                    callback_data=f"status_NOTSTARTED_{project_id}_{task_id}_{position}",
                ),
                InlineKeyboardButton(
                    text="🔵В процессе",
                    callback_data=f"status_INPROGRESS_{project_id}_{task_id}_{position}",
                ),
                InlineKeyboardButton(
                    text="🟢Завершена",
                    callback_data=f"status_COMPLETED_{project_id}_{task_id}_{position}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✏️Изменить задачу",
                    callback_data=f"change_task_{project_id}_{task_id}",
                )
            ],
            [InlineKeyboardButton(text="🔙Назад", callback_data=back_callback_data)],
        ],
    )
    return task_kb


# Keyboards to interact with projects
async def manage_project(project_id):
    """
    Asynchronously creates an inline keyboard markup for managing a project.

    :param project_id: The ID of the project to manage.
    :type project_id: int
    :return: An inline keyboard markup for managing the project.
    :rtype: InlineKeyboardMarkup
    """
    project_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📃Перейти к списку задач",
                    callback_data=f"list_tasks_{project_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️Изменить проект", callback_data="change_project"
                ),
                InlineKeyboardButton(
                    text="➕Новая задача",
                    callback_data=f"new_task_{project_id}_project",
                ),
            ],
            [InlineKeyboardButton(text="🔙Назад", callback_data="list_projects")],
        ],
    )
    return project_kb


async def projects(user_id):
    """
    Asynchronously retrieves all projects associated with the given user ID,
    creates an inline keyboard with the project names and a back button,
    and returns the keyboard markup.

    :param user_id: The ID of the user for whom to retrieve the projects.
    :type user_id: int
    :return: An inline keyboard markup with the project names and a back button.
    :rtype: InlineKeyboardMarkup
    """
    all_projects = await get_projects(user_id)
    keyboard = InlineKeyboardBuilder()
    for project in all_projects:
        if project.name != "General":
            keyboard.add(
                InlineKeyboardButton(
                    text=project.name, callback_data=f"project_{user_id}_{project.id}"
                )
            )
    keyboard.add(
        InlineKeyboardButton(text="➕Новый проект", callback_data="new_project_list")
    )
    keyboard.add(InlineKeyboardButton(text="🔙Назад", callback_data="to_start_kb"))
    return keyboard.adjust(1).as_markup()


async def project_tasks(project_id, user_id):
    """
    Asynchronously retrieves all tasks associated with the given project ID and user ID,
    and creates an inline keyboard with the task names and a back button.

    :param project_id: The ID of the project for which to retrieve the tasks.
    :type project_id: int
    :param user_id: The ID of the user for whom to retrieve the tasks.
    :type user_id: int
    :return: An inline keyboard markup with the task names and a back button.
    :rtype: InlineKeyboardMarkup
    """
    all_tasks = await get_project_tasks(project_id, user_id)
    keyboard = InlineKeyboardBuilder()
    for task in all_tasks:
        task_emoji = await get_task_emoji(task.id, project_id, user_id)
        keyboard.add(
            InlineKeyboardButton(
                text=f"{task_emoji} {task.name}",
                callback_data=f"task_{user_id}_{project_id}_{task.id}_list",
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text="➕Новая задача", callback_data=f"new_task_{project_id}_list"
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="🔙Назад", callback_data=f"project_{user_id}_{project_id}"
        )
    )
    return keyboard.adjust(1).as_markup()


async def general_tasks(project_id, user_id):
    """
    Asynchronously retrieves the project tasks for the given project ID and user ID,
    modifies the callback data of the "🔙Назад" button to "to_start_kb",
    and returns the modified keyboard markup.

    :param project_id: The ID of the project for which to retrieve the tasks.
    :type project_id: int
    :param user_id: The ID of the user for whom to retrieve the tasks.
    :type user_id: int
    :return: An inline keyboard markup with the modified callback data.
    :rtype: InlineKeyboardMarkup
    """
    keyboard = await project_tasks(project_id, user_id)

    # Create a new list to store the modified rows
    new_inline_keyboard = []

    for row in keyboard.inline_keyboard:
        new_row = []
        for button in row:
            # Check if this is the "🔙Назад" button
            if button.callback_data == f"project_{user_id}_{project_id}":
                # Replace the callback_data with "to_start_kb"
                new_button = InlineKeyboardButton(
                    text=button.text, callback_data="to_start_kb"
                )
                new_row.append(new_button)
            elif button.callback_data == f"new_task_{project_id}_list":
                new_button = InlineKeyboardButton(
                    text=button.text, callback_data=f"new_task_{project_id}_general"
                )
                new_row.append(new_button)
            else:
                new_callback_data = button.callback_data + "_general"
                new_button = InlineKeyboardButton(
                    text=button.text, callback_data=new_callback_data
                )
                new_row.append(new_button)
        new_inline_keyboard.append(new_row)

    # Create a new InlineKeyboardMarkup with the modified buttons
    new_keyboard = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    return new_keyboard


async def cancel(user_id, project_id, position):
    """
    Asynchronously creates an inline keyboard markup with a cancel button that has a callback data
    generated using the provided user_id and project_id. The callback data is in the format
    "cancel_{user_id}_{project_id}". The keyboard has a single row with a single button. The button
    text is "✖️Отмена" (which translates to "✖️Cancel" in English).

    :param user_id: The ID of the user.
    :type user_id: int
    :param project_id: The ID of the project.
    :type project_id: int
    :return: An InlineKeyboardMarkup object with the cancel button and callback data.
    :rtype: InlineKeyboardMarkup
    """
    if not project_id:
        project_callback = "none"
    else:
        project_callback = f"{project_id}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✖️Отмена",
                    callback_data=f"cancel_{user_id}_{project_callback}_{position}",
                ),
            ],
        ],
    )
    return keyboard
