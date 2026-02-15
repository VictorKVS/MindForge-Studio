# telegram/bot/main.py

# telegram/bot/main.py
import asyncio
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from telegram.bot.handlers.portrait import router as portrait_router
# from telegram.bot.handlers.ping import router as ping_router  # если есть

async def main():
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing in .env")

    bot = Bot(token=token)
    dp = Dispatcher()

    dp.include_router(portrait_router)
    # dp.include_router(ping_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
