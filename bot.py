"""This is the entry point of the bot"""

import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from app.handlers import router


async def main():
    """Entry point of the bot"""
    load_dotenv()
    bot = Bot(token=str(os.getenv("BOT_TOKEN")))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
