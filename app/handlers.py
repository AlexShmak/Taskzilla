"""This file contains all message handlers for the bot"""

from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command

from app.database.models import Project
import app.text as t
import app.kb as kb
import app.database.requests as rq

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Command /start"""
    await rq.set_user(message.from_user.id)
    await rq.add_project(message.from_user.id, "General")
    await message.reply(t.GREETING, reply_markup=kb.start_kb, parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Command /help"""
    await message.reply(t.HELP, parse_mode="Markdown")


@router.message(Command("luck"))
async def cmd_luck(message: Message):
    """Command /luck"""
    await message.answer_dice(emoji="🎰")


@router.message(F.text == "📝Новая задача")
async def new_task(message: Message):
    """Create a new task"""
    await message.answer("Введите название задачи", reply_markup=ReplyKeyboardRemove())


@router.message(F.text == "📚Новый проект")
async def new_project(message: Message):
    """Creatie a new task"""
    await message.answer("Введите название проекта", reply_markup=ReplyKeyboardRemove())
    # TODO: write new project into the DB


@router.message(F.text == "✅Список общих задач")
async def list_tasks(message: Message):
    """List all tasks"""
    projects = await rq.get_projects(message.from_user.id)
    for project in projects:
        if project.name == "General":
            needed_id = project.id
    await message.answer(
        "Список общих задач",
        reply_markup=await kb.project_tasks(needed_id, message.from_user.id),
    )


@router.message(F.text == "☑️Список проектов")
async def list_projects(message: Message):
    """List all projects"""
    await message.answer(
        "Список проектов", reply_markup=await kb.projects(message.from_user.id)
    )


@router.message(F.text == "🔙Назад")
async def go_back(message: Message):
    """Go back to the main menu"""
    await message.answer("Возвращаю в главное меню", reply_markup=kb.start_kb)
