import asyncio
import time
from aiogram import Bot
from config import BOT_TOKEN
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import NetworkError
import aioschedule





bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)



        

if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp
    from mailing.functions import mailing_dishe

    

    async def scheduler():
        # aioschedule.every().day.at("08:30").do(mailing_dishe)
        aioschedule.every(1).seconds.do(mailing_dishe) # test
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)



    async def on_startup(dp): 
        asyncio.create_task(scheduler())

    print('✅ bot is run')
    while 1:
        try:
            executor.start_polling(dp, on_startup=on_startup)

        except NetworkError:
            print(f'reconecting')
            time.sleep(1)
    