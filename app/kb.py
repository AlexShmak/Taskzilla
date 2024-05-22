"""This file contains all keyboars for the bot"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
