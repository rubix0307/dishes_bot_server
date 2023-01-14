

from aiogram import types
from app import bot, dp
from functions import by_categories, by_countries, contest, groups, start
from aiogram.dispatcher import FSMContext

from handlers.admin.functions import edit_categories, edit_categories_cancel


br = '\n'
@dp.message_handler(state='*', commands=['edit_categories'])
async def edit_categories_handler(message: types.Message, state=FSMContext):
    await edit_categories(message, state)

@dp.message_handler(state='EditCategories:active', commands=['stop'])
async def edit_categories_cancel_handler(message: types.Message, state=FSMContext):
    await edit_categories_cancel(message, state)