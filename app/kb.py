"""This file contains all keyboars for the bot"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import get_projects, get_project_tasks

# General keyboards
start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝Новая задача"), KeyboardButton(text="📚Новый проект")],
        [KeyboardButton(text="✅Список общих задач")],
        [KeyboardButton(text="☑️Список проектов")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие...",
)


change_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝Переименовать"), KeyboardButton(text="❌Удалить")],
        [KeyboardButton(text="🔙Назад")],
    ]
)


# Keyboards to interact with tasks
task_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🟣Не начата"),
            KeyboardButton(text="🔵В процессе"),
            KeyboardButton(text="🟢Завершена"),
        ],
        [KeyboardButton(text="✏️Изменить задачу")],
    ]
)


# Keyboards to interact with projects
project_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️Изменить проект")],
        [KeyboardButton(text="📃Перейти к списку задач")],
    ]
)


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
        keyboard.add(
            InlineKeyboardButton(
                text=project.name, callback_data=f"project{user_id}_{project.id}"
            )
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
        keyboard.add(
            InlineKeyboardButton(
                text=task.name, callback_data=f"task_{user_id}_{project_id}_{task.id}"
            )
        )
    keyboard.add(InlineKeyboardButton(text="🔙Назад", callback_data="to_start_kb"))
    return keyboard.adjust(1).as_markup()
