
import asyncio
import time

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import NetworkError

from config import BOT_TOKEN



storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

if __name__ == '__main__':
    from aiogram import executor
    from functions.admin import scheduler
    from handlers import dp

    async def on_startup(dp):
        print('✅ Bot is run')
        asyncio.create_task(scheduler())
        

    while 1:
        try:
            executor.start_polling(dp, on_startup=on_startup)
        except NetworkError:
            print(f'reconecting')
            time.sleep(1)
