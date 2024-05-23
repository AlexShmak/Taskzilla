"""This file contains all message handlers for the bot"""

from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
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
        project (State): The project that the bot is currently working on.
    """

    waiting_for_task_name = State()
    waiting_for_project_name = State()


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


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Command /help"""
    await message.reply(t.HELP, parse_mode="Markdown")


@router.message(Command("luck"))
async def cmd_luck(message: Message):
    """Command /luck"""
    await message.answer_dice(emoji="🎰")


@router.callback_query(F.data.startswith("new_task_"))
async def new_task(callback: CallbackQuery, state: FSMContext):
    """Create a new task"""
    await callback.answer("Создание новой задачи")
    await state.set_state(States.waiting_for_task_name)
    await state.update_data(
        project_id=callback.data.split("_")[2], message_id=callback.message.message_id
    )
    await callback.message.edit_text("Введите название задачи")


@router.message(States.waiting_for_task_name)
async def create_new_task(message: Message, state: FSMContext):
    """Create a new task"""
    data = await state.get_data()
    await rq.add_task(data["project_id"], message.text, message.from_user.id)
    await state.clear()
    await message.delete()
    await message.bot.delete_message(message.chat.id, message_id=data["message_id"])
    if rq.project_is_general(data["project_id"], message.from_user.id):
        await message.answer(
            f'Задача "{message.text}" создана',
            reply_markup=await kb.general_tasks(
                data["project_id"], message.from_user.id
            ),
        )
    else:
        await message.answer(
            f'Задача "{message.text}" создана',
            reply_markup=await kb.project_tasks(
                data["project_id"], message.from_user.id
            ),
        )


@router.callback_query(F.data.startswith("task_"))
async def task(callback: CallbackQuery):
    """Manage a task"""
    await callback.answer("Вы выбрали задачу")
    await callback.message.edit_text(
        "Вы выбрали задачу", reply_markup=await kb.manage_task
    )


@router.callback_query(F.data == "new_project")
async def new_project(callback: CallbackQuery, state: FSMContext):
    """Create a new task"""
    await callback.answer("Создание нового проекта")
    await state.set_state(States.waiting_for_project_name)
    await callback.message.edit_text(
        "Введите название проекта", reply_markup=ReplyKeyboardRemove()
    )


@router.callback_query(F.data == "list_general_tasks")
async def list_general_tasks(callback: CallbackQuery):
    """List all general tasks"""
    await callback.answer("Список общих задач")
    projects = await rq.get_projects(callback.from_user.id)
    for project in projects:
        if project.name == "General":
            needed_id = project.id
    await callback.message.edit_text(
        "Список общих задач",
        reply_markup=await kb.general_tasks(needed_id, callback.from_user.id),
    )


@router.callback_query(F.data.startswith("list_tasks_"))
async def list_tasks(callback: CallbackQuery):
    """List all tasks"""
    await callback.answer("Список задач")
    await callback.message.edit_text(
        "Список общих задач",
        reply_markup=await kb.project_tasks(
            callback.data.split("_")[2], callback.from_user.id
        ),
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
    project_name = await rq.get_project_name(
        callback.data.split("_")[2], callback.data.split("_")[1]
    )
    await callback.answer(f"Вы выбрали проект: {project_name}")
    await callback.message.edit_text(
        f"Проект: {project_name}",
        reply_markup=await kb.manage_project(callback.data.split("_")[2]),
    )


@router.callback_query(F.data == "to_start_kb")
async def go_back(callback: CallbackQuery):
    """Go back to the main menu"""
    await callback.answer("Возвращаю в главное меню")
    await callback.message.edit_text(
        "Главное меню", reply_markup=await kb.starting_kb(callback.from_user.id)
    )


# TODO: adding new project
# FIXME: transition between keyboards
