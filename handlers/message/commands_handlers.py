

from aiogram import types
from app import bot, dp
from functions import by_categories, by_countries, contest, groups, start


br = '\n'
@dp.message_handler(state='*', commands=['start'])
async def main_def(message: types.Message):
    await start(message)
    
@dp.message_handler(state='*', commands=['categories'])
async def groups_command(message: types.Message, is_callback=False):
    await by_categories(bot, message)

@dp.message_handler(state='*', commands=['countries'])
async def groups_command(message: types.Message, is_callback=False):
    await by_countries(bot, message)

@dp.message_handler(state='*', commands=['groups'])
async def groups_command(message: types.Message, is_callback=False):
    await groups(message, is_callback)
   
@dp.message_handler(state='*', commands=['contest'])
async def contest_handler(message: types.Message, is_callback=False):
    await contest(message, is_callback)