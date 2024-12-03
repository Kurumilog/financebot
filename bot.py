import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher

from handlers.user_commands import user_private_router
from handlers.user_register import user_register_router
from handlers.report import report_router
from handlers.transaction import transaction_router
from handlers.pagination import pagination_router

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()
dp.include_router(user_private_router)
dp.include_router(user_register_router)
dp.include_router(report_router)
dp.include_router(transaction_router)
dp.include_router(pagination_router)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
