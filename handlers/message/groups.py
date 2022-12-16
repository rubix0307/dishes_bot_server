

from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.markdown import hlink, hunderline, hbold
from app import bot, dp
from config import ADMIN_ID, BOT_URL
from db.functions import sql
from functions import groups, update_last_message, user_activity_record
from markups import call_filters, get_home_button, get_nothing_button

br = '\n'

@dp.message_handler(state='*', commands=['groups'])
async def groups_command(message: types.Message, is_callback=False):
    await groups(message, is_callback)
   