from aiogram import types

from app import dp, bot
from config import ADMIN_ID
from db.functions import sql
from functions import get_home_page, register_user, update_last_message
from mailing.functions import subscribe_to_group


@dp.message_handler(state='*', commands=['group'])
async def main_def(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await subscribe_to_group()