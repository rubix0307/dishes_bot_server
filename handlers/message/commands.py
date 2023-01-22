from aiogram import types

from app import bot, dp
from functions.main import (by_categories, by_countries, contest, groups,
                            start, user_activity_record)


@dp.message_handler(state='*', commands=['start'])
async def main_def(message: types.Message):
    user_activity_record(message.from_user.id, '0', 'command: start')
    await start(message)
    
@dp.message_handler(state='*', commands=['categories'])
async def groups_command(message: types.Message):
    user_activity_record(message.from_user.id, '0', 'command: categories')
    await by_categories(bot, message)

@dp.message_handler(state='*', commands=['countries'])
async def groups_command(message: types.Message):
    user_activity_record(message.from_user.id, '0', 'command: countries')
    await by_countries(bot, message)

@dp.message_handler(state='*', commands=['groups'])
async def groups_command(message: types.Message, is_callback=False):
    user_activity_record(message.from_user.id, '0', 'command: groups')
    await groups(message, is_callback)
   
@dp.message_handler(state='*', commands=['contest'])
async def contest_handler(message: types.Message, is_callback=False):
    user_activity_record(message.from_user.id, '0', 'command: contest')
    await contest(message, is_callback)