"""This file contains all message handlers for the bot"""

from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.text as t
from app import kb


router = Router()


class Reg(StatesGroup):
    """State for checking registration"""

    id = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Command /start"""
    await message.reply(t.GREETING, reply_markup=kb.start_kb, parse_mode="Markdown")
    # TODO: write new user into the DB


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
    """Creatie a new task"""
    await message.answer("Введите название задачи", reply_markup=ReplyKeyboardRemove())
    # TODO: write new task into the DB


@router.message(F.text == "📚Новый проект")
async def new_project(message: Message):
    """Creatie a new task"""
    await message.answer("Введите название проекта", reply_markup=ReplyKeyboardRemove())
    # TODO: write new project into the DB


@router.message(F.text == "✅Список общих задач")
async def list_tasks(message: Message):
    """List all tasks"""
    # TODO: list all tasks


@router.message(F.text == "☑️Список проектов")
async def list_projects(message: Message):
    """List all projects"""
    # TODO: list all projects


@router.message(F.text == "🔙Назад")
async def go_back(message: Message):
    """Go back to the main menu"""
    await message.answer("Возвращаю в главное меню", reply_markup=kb.start_kb)
