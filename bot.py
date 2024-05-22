import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from app.handlers import router

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def main():
    load_dotenv()
    bot = Bot(os.getenv("BOT_TOKEN"), parse_mode="Markdown")
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
