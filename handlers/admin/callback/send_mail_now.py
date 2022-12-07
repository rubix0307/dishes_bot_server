import time
from aiogram import types

from app import dp
from mailing.functions import mailing_dishe
from markups import mail_now


@dp.callback_query_handler(mail_now.filter())
async def mail_now(call: types.CallbackQuery, callback_data: dict()):

    dish_id = int(callback_data['dish_id'])

    await mailing_dishe(castom_dish_id = dish_id)
    await call.answer('✅ Отправлено')

