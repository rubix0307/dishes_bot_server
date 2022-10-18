from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from app import dp
from config import BOT_URL
from db.functions import sql
from functions import get_home_button, update_last_message



@dp.message_handler()
async def main_def(message: types.Message):
    text = message.html_text

    if not BOT_URL in text:
        data_list = sql(
            f'SELECT * FROM dishes WHERE title LIKE "%{text}%" LIMIT 1')

        if len(data_list) and type(data_list) == list:
            dish = InlineKeyboardButton(
                    text=f'Блюдо: {message.text.lower()}',
                    switch_inline_query_current_chat=message.text
                )

            markup = InlineKeyboardMarkup()
            markup.add(dish)

            message_data = {
                'text': 'Возможно вы искали это:',
                'reply_markup': markup,
            }

            await message.answer(**message_data)
        
        else:
            keyboard_markup = InlineKeyboardMarkup()
            keyboard_markup.add(get_home_button())
            await message.answer('Я вас не понял.', reply_markup=keyboard_markup)
        
        await update_last_message(message, castom_message_id=message.message_id + 1)
        await message.delete()
    else:
        await update_last_message(message)
