from aiogram import types

from app import bot, dp
from functions.admin import get_stats_by_after_hour_subs


@dp.message_handler(state='*', commands=['get_stats_by_after_hour_subs'])
async def main_def(message: types.Message):
    await get_stats_by_after_hour_subs(message)
