from aiogram import types

from app import bot, dp
from functions.main import (by_categories, by_countries, contest, groups,
                            start, user_activity_record)


@dp.message_handler(state='*', commands=['start'])
async def main_def(message: types.Message):
    user_activity_record(message.from_user.id, '0', 'command: start')
    await start(message)
