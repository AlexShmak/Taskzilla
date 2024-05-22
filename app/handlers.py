from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.text as t


router = Router()


class Reg(StatesGroup):
    id = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.reply(t.greeting)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(t.help)


@router.message(Command("luck"))
async def cmd_luck(message: Message):
    await message.answer_dice(emoji="🎰")
