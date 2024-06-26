"""This file contains all message handlers for the bot"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.text as t
import app.kb as kb
import app.database.requests as rq


router = Router()


class States(StatesGroup):
    """
    Contains all states that the bot can be in.

    Attributes:
        waiting_for_task_name (State): The state where the bot
            is waiting for the user to input a task name.
        waiting_for_project_name (State): The state where the bot
            is waiting for the user to input a project name.
    """

    waiting_for_task_name = State()
    waiting_for_project_name = State()

    waiting_for_new_task_name = State()
    waiting_for_new_project_name = State()

    waiting_for_comment = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Command /start"""
    await rq.add_user(message.from_user.id)
    await rq.add_project(message.from_user.id, "General")
    await message.answer(
        t.GREETING,
        reply_markup=await kb.starting_kb(message.from_user.id),
        parse_mode="Markdown",
    )


@router.message(
    F.content_type.in_(
        {
            "sticker",
            "animation",
            "video_note",
            "voice",
            "video",
            "photo",
            "document",
            "game",
            "story",
            "autio",
            "contact",
            "dice",
            "poll",
            "location",
            "venue",
            "new_chat_members",
            "left_chat_member",
            "new_chat_title",
            "new_chat_photo",
            "delete_chat_photo",
            "group_chat_created",
            "supergroup_chat_created",
            "channel_chat_created",
            "migrate_to_chat_id",
            "migrate_from_chat_id",
            "pinned_message",
            "invoice",
            "successful_payment",
            "passport_data",
        }
    )
)
async def filter_trash(message: Message):
    """Filter trash messages"""
    await message.delete()


# Handling messages related to TASKS
@router.callback_query(F.data.startswith("new_task_"))
async def new_task(callback: CallbackQuery, state: FSMContext):
    """Create a new task: asking for task name"""
    await callback.answer("Создание новой задачи")
    await state.set_state(States.waiting_for_task_name)
    project_id = callback.data.split("_")[2]
    position = callback.data.split("_")[3]
    await state.update_data(
        project_id=project_id, message_id=callback.message.message_id, position=position
    )
    await callback.message.edit_text(
        "Введите название задачи",
        reply_markup=await kb.cancel(callback.from_user.id, project_id, position),
    )


@router.message(States.waiting_for_task_name)
async def create_new_task(message: Message, state: FSMContext):
    """Create a new task: receiving task name"""
    data = await state.get_data()
    project_name = await rq.get_project_name(data["project_id"], message.from_user.id)
    project_id = data["project_id"]
    await rq.add_task(project_id, f"{message.text}", message.from_user.id)
    task_id = await rq.get_task_id(message.text, project_id, message.from_user.id)
    task_emoji = await rq.get_task_emoji(task_id, project_id, message.from_user.id)
    await message.delete()
    await message.bot.delete_message(message.chat.id, message_id=data["message_id"])
    if data["position"] == "general":
        await message.answer(
            f'Задача "{task_emoji} {message.text}" в общих задачах создана',
            reply_markup=await kb.general_tasks(project_id, message.from_user.id),
        )
    elif data["position"] == "list":
        await message.answer(
            f'Задача "{task_emoji} {message.text}" в проекте "{project_name}" создана',
            reply_markup=await kb.project_tasks(project_id, message.from_user.id),
        )
    elif data["position"] == "project":
        await message.answer(
            f'Задача "{task_emoji} {message.text}" в проекте "{project_name}" создана',
            reply_markup=await kb.manage_project(project_id),
        )
    await state.clear()


@router.callback_query(F.data.startswith("task_"))
async def task(callback: CallbackQuery):
    """Manage a task"""
    project_id = callback.data.split("_")[2]
    task_id = callback.data.split("_")[3]
    task_name = await rq.get_task_name(task_id, project_id, callback.from_user.id)
    task_emoji = await rq.get_task_emoji(task_id, project_id, callback.from_user.id)
    project_name = await rq.get_project_name(project_id, callback.from_user.id)
    position = callback.data.split("_")[-1]
    comment = await rq.get_task_comment(task_id, project_id, callback.from_user.id)
    if not comment:
        comment = "Комментарий пока не добавлен"
    if position == "general":
        back_callback_data = "list_general_tasks"
        answer = f'Вы выбрали задачу "{task_emoji} {task_name}" в общих задачаx\n\nКомментарий: "{comment}"'
    elif position == "list":
        back_callback_data = f"list_tasks_{project_id}"
        answer = f'Вы выбрали задачу "{task_emoji} {task_name}" в проекте "{project_name}"\n\nКомментарий: "{comment}"'
    await callback.answer(answer)
    await callback.message.edit_text(
        answer,
        reply_markup=await kb.manage_task(
            project_id, task_id, back_callback_data, position
        ),
    )


@router.callback_query(F.data.startswith("add_comment_"))
async def add_comment(callback: CallbackQuery, state: FSMContext):
    """Add comment"""
    project_id = callback.data.split("_")[2]
    task_id = callback.data.split("_")[3]
    position = callback.data.split("_")[4]
    task_name = await rq.get_task_name(task_id, project_id, callback.from_user.id)
    await callback.answer("Добавление комментария")
    await state.set_state(States.waiting_for_comment)
    await state.update_data(
        project_id=project_id,
        task_id=task_id,
        message_id=callback.message.message_id,
        position=position,
    )
    await callback.message.edit_text(
        f'Введите комментарий для задачи "{task_name}"',
        reply_markup=await kb.cancel_changing_comment(project_id, task_id, position),
    )


@router.callback_query(F.data.startswith("cancelChangingComment_"))
async def cancel_changing_comment(callback: CallbackQuery, state: FSMContext):
    """Cancel changing comment"""
    await state.clear()
    project_id = callback.data.split("_")[1]
    task_id = callback.data.split("_")[2]
    position = callback.data.split("_")[3]
    task_name = await rq.get_task_name(task_id, project_id, callback.from_user.id)
    task_emoji = await rq.get_task_emoji(task_id, project_id, callback.from_user.id)
    comment = await rq.get_task_comment(task_id, project_id, callback.from_user.id)
    if not comment:
        comment = "Комментарий пока не добавлен"
    await callback.answer("Отмена")
    if position == "general":
        await callback.message.edit_text(
            f'Вы выбрали задачу "{task_emoji} {task_name}" в общих задачах\n\nКомментарий: "{comment}"',
            reply_markup=await kb.manage_task(
                project_id, task_id, "list_general_tasks", "general"
            ),
        )
    else:
        project_name = await rq.get_project_name(project_id, callback.from_user.id)
        await callback.message.edit_text(
            f'Вы выбрали задачу "{task_emoji} {task_name}" в проекте "{project_name}"\n\nКомментарий: "{comment}"',
            reply_markup=await kb.manage_task(
                project_id, task_id, "list_tasks_" + project_id, "list"
            ),
        )


@router.message(States.waiting_for_comment)
async def add_comment_name(message: Message, state: FSMContext):
    """Add comment: receiving comment name"""
    data = await state.get_data()
    task_id = data["task_id"]
    project_id = data["project_id"]
    position = data["position"]
    project_name = await rq.get_project_name(project_id, message.from_user.id)
    task_name = await rq.get_task_name(task_id, project_id, message.from_user.id)
    task_emoji = await rq.get_task_emoji(task_id, project_id, message.from_user.id)
    comment = message.text
    await rq.chgange_task_comment(task_id, project_id, message.from_user.id, comment)
    await message.delete()
    await message.bot.delete_message(message.chat.id, message_id=data["message_id"])
    if position == "general":
        back_callback_data = "list_general_tasks"
        answer = f'Вы выбрали задачу "{task_emoji} {task_name}" в общих задачаx\n\nКомментарий: "{comment}"'
    else:
        back_callback_data = f"list_tasks_{project_id}"
        answer = f'Вы выбрали задачу "{task_emoji} {task_name}" в проекте "{project_name}"\n\nКомментарий: "{comment}"'
    await message.answer(
        answer,
        reply_markup=await kb.manage_task(
            project_id, task_id, back_callback_data, position
        ),
    )
    await state.clear()


@router.callback_query(F.data.startswith("change_task_"))
async def change_task(callback: CallbackQuery):
    """Change task"""
    project_id = callback.data.split("_")[2]
    task_id = callback.data.split("_")[3]
    position = callback.data.split("_")[4]
    await callback.answer("Изменение задачи")
    await callback.message.edit_reply_markup(
        reply_markup=await kb.change_task_kb(
            callback.from_user.id, project_id, task_id, position
        )
    )


@router.callback_query(F.data.startswith("delete_task_"))
async def delete_task(callback: CallbackQuery):
    """Delete task"""
    project_id = callback.data.split("_")[2]
    task_id = callback.data.split("_")[3]
    position = callback.data.split("_")[4]
    await callback.answer("Удаление задачи")
    await rq.delete_task(task_id, project_id, callback.from_user.id)
    project_name = await rq.get_project_name(project_id, callback.from_user.id)
    if position == "general":
        text = "Cписок общих задач"
        keyboard = await kb.general_tasks(project_id, callback.from_user.id)
    else:
        keyboard = await kb.project_tasks(project_id, callback.from_user.id)
        text = f'Список задач проекта "{project_name}"'
    await callback.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("rename_task_"))
async def rename_task(callback: CallbackQuery, state: FSMContext):
    """Rename task: asking for new task name"""
    project_id = callback.data.split("_")[2]
    task_id = callback.data.split("_")[3]
    position = callback.data.split("_")[4]
    await callback.answer("Переименование задачи")
    await state.set_state(States.waiting_for_new_task_name)
    await state.update_data(
        {
            "project_id": project_id,
            "task_id": task_id,
            "position": position,
            "message_id": callback.message.message_id,
        }
    )
    await callback.message.edit_text(
        "Введите новое название задачи",
        reply_markup=await kb.cancel_renaming_task(project_id, task_id, position),
    )


@router.message(States.waiting_for_new_task_name)
async def rename_task_name(message: Message, state: FSMContext):
    """Rename task: receiving new task name"""
    data = await state.get_data()
    position = data["position"]
    await rq.rename_task(
        data["task_id"], data["project_id"], message.from_user.id, message.text
    )
    if position == "general":
        await message.delete()
        await message.bot.delete_message(message.chat.id, message_id=data["message_id"])
        await message.answer(
            f'Список общих задач\n\nЗадача "{message.text}" переименована',
            reply_markup=await kb.general_tasks(
                data["project_id"], message.from_user.id
            ),
        )
    else:
        project_name = await rq.get_project_name(
            data["project_id"], message.from_user.id
        )
        await message.delete()
        await message.bot.delete_message(message.chat.id, message_id=data["message_id"])
        await message.answer(
            f'Список задач проекта "{project_name}"\n\nЗадача "{message.text}" переименована',
            reply_markup=await kb.project_tasks(
                data["project_id"], message.from_user.id
            ),
        )
    await state.clear()


@router.callback_query(F.data.startswith("cancelRenamingTask_"))
async def cancel_renaming_task(callback: CallbackQuery, state: FSMContext):
    """Cancel renaming task"""
    await state.clear()
    project_id = callback.data.split("_")[1]
    task_id = callback.data.split("_")[2]
    position = callback.data.split("_")[3]
    task_name = await rq.get_task_name(task_id, project_id, callback.from_user.id)
    task_emoji = await rq.get_task_emoji(task_id, project_id, callback.from_user.id)
    comment = await rq.get_task_comment(task_id, project_id, callback.from_user.id)
    if not comment:
        comment = "Комментарий пока не добавлен"
    await callback.answer("Отмена")
    if position == "general":
        await callback.message.edit_text(
            f'Вы выбрали задачу "{task_emoji} {task_name}" в общих задачах\n\nКомментарий: "{comment}"',
            reply_markup=await kb.manage_task(
                project_id, task_id, "list_general_tasks", "general"
            ),
        )
    else:
        project_name = await rq.get_project_name(project_id, callback.from_user.id)
        await callback.message.edit_text(
            f'Вы выбрали задачу "{task_emoji} {task_name}" в проекте "{project_name}"\n\nКомментарий: "{comment}"',
            reply_markup=await kb.manage_task(
                project_id, task_id, "list_tasks_" + project_id, "list"
            ),
        )


@router.callback_query(F.data == "list_general_tasks")
async def list_general_tasks(callback: CallbackQuery):
    """List all general tasks"""
    await callback.answer("Список общих задач")
    general_project_id = await rq.get_general_project_id(callback.from_user.id)
    await callback.message.edit_text(
        "Список общих задач",
        reply_markup=await kb.general_tasks(general_project_id, callback.from_user.id),
    )


@router.callback_query(F.data.startswith("list_tasks_"))
async def list_tasks(callback: CallbackQuery):
    """List all tasks"""
    project_id = callback.data.split("_")[2]
    project_name = await rq.get_project_name(project_id, callback.from_user.id)
    await callback.answer("Список задач")
    await callback.message.edit_text(
        f'Список задач проекта "{project_name}"',
        reply_markup=await kb.project_tasks(project_id, callback.from_user.id),
    )


@router.callback_query(F.data.startswith("status_"))
async def status(callback: CallbackQuery):
    """Change task status"""
    callback_data_list = callback.data.split("_")
    new_status = callback_data_list[1]
    project_id = callback_data_list[2]
    task_id = callback_data_list[3]
    position = callback_data_list[4]
    task_name = await rq.get_task_name(task_id, project_id, callback.from_user.id)
    project_name = await rq.get_project_name(project_id, callback.from_user.id)
    comment = await rq.get_task_comment(task_id, project_id, callback.from_user.id)
    if not comment:
        comment = "Комментарий пока не добавлен"
    await callback.answer("Статус задачи изменен")
    if new_status == "NOTSTARTED":
        await rq.change_task_status_to_notstarted(
            task_id, project_id, callback.from_user.id, new_status
        )
    if new_status == "INPROGRESS":
        await rq.change_task_status_to_inprogress(
            task_id, project_id, callback.from_user.id, new_status
        )
    if new_status == "COMPLETED":
        await rq.change_task_status_to_completed(
            task_id, project_id, callback.from_user.id, new_status
        )
    task_emoji = await rq.get_task_emoji(task_id, project_id, callback.from_user.id)
    if position == "general":
        await callback.message.edit_text(
            f'Вы выбрали задачу "{task_emoji} {task_name}" в общих задачах\n\nКомментарий: "{comment}"',
            reply_markup=await kb.manage_task(
                project_id, task_id, "list_general_tasks", "general"
            ),
        )
    else:
        await callback.message.edit_text(
            f'Вы выбрали задачу "{task_emoji} {task_name}" в проекте "{project_name}"\n\nКомментарий: "{comment}"',
            reply_markup=await kb.manage_task(
                project_id, task_id, f"list_tasks_{project_id}", "list"
            ),
        )


# Handling messages related to PROJECTS
@router.callback_query(F.data.startswith("new_project_"))
async def new_project(callback: CallbackQuery, state: FSMContext):
    """Create a new project: asking for project name"""
    await callback.answer("Создание нового проекта")
    await state.set_state(States.waiting_for_project_name)
    await state.update_data(message_id=callback.message.message_id)
    position = callback.data.split("_")[-1]
    await callback.message.edit_text(
        "Введите название проекта",
        reply_markup=await kb.cancel(callback.from_user.id, None, position),
    )


@router.message(States.waiting_for_project_name)
async def create_new_project(message: Message, state: FSMContext):
    """Create a new project: receiving project name"""
    data = await state.get_data()
    project_name = message.text
    if project_name == "General":
        await state.clear()
        await message.delete()
        await message.bot.delete_message(message.chat.id, message_id=data["message_id"])
        await message.answer(
            "Cписок проектов\n\nОшибка: Нельзя использовать название 'General'",
            reply_markup=await kb.projects(message.from_user.id),
        )
    else:
        await rq.add_project(message.from_user.id, message.text)
        await state.clear()
        await message.delete()
        await message.bot.delete_message(message.chat.id, message_id=data["message_id"])
        await message.answer(
            f'Проект "{project_name}" создан',
            reply_markup=await kb.projects(message.from_user.id),
        )


@router.callback_query(F.data == "list_projects")
async def list_projects(callback: CallbackQuery):
    """List all projects"""
    await callback.answer("Список проектов")
    await callback.message.edit_text(
        "Список проектов", reply_markup=await kb.projects(callback.from_user.id)
    )


@router.callback_query(F.data.startswith("project_"))
async def manage_project(callback: CallbackQuery):
    """Manage a project"""
    project_id = callback.data.split("_")[2]
    project_name = await rq.get_project_name(project_id, callback.from_user.id)
    await callback.answer(f'Вы выбрали проект "{project_name}"')
    await callback.message.edit_text(
        f"Проект: {project_name}", reply_markup=await kb.manage_project(project_id)
    )


@router.callback_query(F.data.startswith("change_project_"))
async def change_project(callback: CallbackQuery):
    """Change project"""
    project_id = callback.data.split("_")[2]
    await callback.answer("Изменение проекта")
    await callback.message.edit_reply_markup(
        reply_markup=await kb.change_project_kb(project_id, callback.from_user.id)
    )


@router.callback_query(F.data.startswith("delete_project_"))
async def delete_project(callback: CallbackQuery):
    """Delete project"""
    project_id = callback.data.split("_")[2]
    await callback.answer("Удаление проекта")
    await rq.delete_project(project_id, callback.from_user.id)
    await callback.message.edit_text(
        "Список проектов", reply_markup=await kb.projects(callback.from_user.id)
    )


@router.callback_query(F.data.startswith("rename_project_"))
async def rename_project(callback: CallbackQuery, state: FSMContext):
    """Rename project: asking for new project name"""
    project_id = callback.data.split("_")[2]
    await callback.answer("Переименование проекта")
    await state.set_state(States.waiting_for_new_project_name)
    await state.update_data(
        project_id=project_id, message_id=callback.message.message_id
    )
    await callback.message.edit_text(
        "Введите новое название проекта",
        reply_markup=await kb.cancel_renaming_project(project_id),
    )


@router.message(States.waiting_for_new_project_name)
async def rename_project_name(message: Message, state: FSMContext):
    """Rename project: receiving new project name"""
    data = await state.get_data()
    await rq.rename_project(data["project_id"], message.from_user.id, message.text)
    await message.delete()
    await message.bot.delete_message(message.chat.id, message_id=data["message_id"])
    await message.answer(
        f'Проект "{message.text}" переименован',
        reply_markup=await kb.projects(message.from_user.id),
    )
    await state.clear()


@router.callback_query(F.data.startswith("cancelRenamingProject_"))
async def cancel_renaming_project(callback: CallbackQuery):
    """Cancel renaming project"""
    project_id = callback.data.split("_")[1]
    project_name = await rq.get_project_name(project_id, callback.from_user.id)
    await callback.answer("Отмена")
    await callback.message.edit_text(
        f'Вы выбрали проект "{project_name}"',
        reply_markup=await kb.manage_project(project_id),
    )


@router.callback_query(F.data.startswith("cancel_"))
async def cancel(callback: CallbackQuery):
    """Cancel"""
    cancel_callback = callback.data.split("_")
    user_id = cancel_callback[1]
    project_callback = cancel_callback[2]
    position = cancel_callback[3]
    await callback.answer("Отмена")

    if project_callback == "none":
        if position == "list":
            await callback.message.edit_text(
                "Список проектов", reply_markup=await kb.projects(user_id)
            )
        else:
            await callback.message.edit_text(
                "Главное меню", reply_markup=await kb.starting_kb(user_id)
            )
    else:
        if position == "general":
            await callback.message.edit_text(
                "Главное меню", reply_markup=await kb.starting_kb(user_id)
            )
        elif position == "list":
            project_name = await rq.get_project_name(project_callback, user_id)
            await callback.message.edit_text(
                f'Список задач проекта "{project_name}"',
                reply_markup=await kb.project_tasks(project_callback, user_id),
            )
        elif position == "project":
            project_name = await rq.get_project_name(project_callback, user_id)
            await callback.message.edit_text(
                f'Вы выбрали проект "{project_name}"',
                reply_markup=await kb.manage_project(project_callback),
            )
        else:
            await callback.message.edit_text(
                "Список общих задач",
                reply_markup=await kb.general_tasks(project_callback, user_id),
            )


@router.callback_query(F.data == "to_start_kb")
async def go_back(callback: CallbackQuery):
    """Go back to the main menu"""
    await callback.answer("Возвращаю в главное меню")
    await callback.message.edit_text(
        "Главное меню", reply_markup=await kb.starting_kb(callback.from_user.id)
    )


@router.message(
    F.content_type.in_(
        {
            "text",
        }
    )
)
async def filter_trash_text(message: Message):
    """Filter trash messages"""
    await message.delete()
