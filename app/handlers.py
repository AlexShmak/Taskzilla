"""This file contains all message handlers for the bot"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
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


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Command /start"""
    await message.delete()
    await rq.add_user(message.from_user.id)
    await rq.add_project(message.from_user.id, "General")
    await message.answer(
        t.GREETING,
        reply_markup=await kb.starting_kb(message.from_user.id),
        parse_mode="Markdown",
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Command /help"""
    await message.reply(t.HELP, parse_mode="Markdown")


@router.message(Command("luck"))
async def cmd_luck(message: Message):
    """Command /luck"""
    await message.answer_dice(emoji="🎰")


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
    await rq.add_task(data["project_id"], f"🟣 {message.text}", message.from_user.id)
    await message.delete()
    await message.bot.delete_message(message.chat.id, message_id=data["message_id"])
    if data["position"] == "general":
        await message.answer(
            f'Задача "{message.text}" в общих задачах создана',
            reply_markup=await kb.general_tasks(project_id, message.from_user.id),
        )
    elif data["position"] == "list":
        await message.answer(
            f'Задача "{message.text}" в проекте "{project_name}" создана',
            reply_markup=await kb.project_tasks(project_id, message.from_user.id),
        )
    elif data["position"] == "project":
        await message.answer(
            f'Задача "{message.text}" в проекте "{project_name}" создана',
            reply_markup=await kb.manage_project(project_id),
        )
    await state.clear()


@router.callback_query(F.data.startswith("task_"))
async def task(callback: CallbackQuery):
    """Manage a task"""
    project_id = callback.data.split("_")[2]
    task_id = callback.data.split("_")[3]
    task_name = await rq.get_task_name(task_id, project_id, callback.from_user.id)
    project_name = await rq.get_project_name(project_id, callback.from_user.id)
    position = callback.data.split("_")[-1]
    if position == "general":
        back_callback_data = "list_general_tasks"
        answer = f"Вы выбрали задачу '{task_name}' в общих задачаx"
        print("\ntrue\n")
    elif position == "list":
        back_callback_data = f"list_tasks_{project_id}"
        answer = f"Вы выбрали задачу '{task_name}' в проекте '{project_name}'"
        print("\nfalse\n")
    await callback.answer(answer)
    await callback.message.edit_text(
        answer,
        reply_markup=await kb.manage_task(project_id, task_id, back_callback_data),
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
    await rq.add_project(message.from_user.id, message.text)
    await state.clear()
    await message.delete()
    await message.bot.delete_message(message.chat.id, message_id=data["message_id"])
    await message.answer(
        f'Проект "{message.text}" создан',
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
                f"Список задач проекта '{project_name}'",
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


# FIXME: transition inside general project
# NOTE: forbid users to delete general project (they shouldn't be able to even see it)
# NOTE: forbid users to create project with name GENERAL
