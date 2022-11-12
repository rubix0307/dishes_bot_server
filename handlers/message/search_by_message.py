from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.exceptions import MessageToDeleteNotFound

from app import dp
from config import BOT_URL, MEDIA_URL
from db.functions import sql
from functions import (Article, get_data_dish, get_fav_ids, get_home_button,
                       update_last_message, user_activity_record)
from . import get_by_id

@dp.message_handler()
async def main_def(message: types.Message):
    markup = InlineKeyboardMarkup()
    text = message.html_text
    user = message.from_user

    if not BOT_URL in text:
        if text.isdigit():
            dish_id = int(text)

            try:
                await message.delete()
            except MessageToDeleteNotFound:
                pass
            
            try:
                data = get_data_dish(dish_id)
            except:
                await message.answer('Я вас не понял.', reply_markup=InlineKeyboardMarkup().add(get_home_button()))
            
            article = Article(data, user_id=user.id)
            try:
                article.preview = MEDIA_URL + data['local_photo']
            except:
                pass
                
            try:
                await update_last_message(message, castom_message_id=message.message_id + 1)
                await message.answer(reply_markup=article.get_markup(), text=article.get_message_text(), parse_mode='html')
    
            finally:
                user_activity_record(user.id, dish_id, text)
                return

        elif not BOT_URL in text:
            title = f'Блюдо содержит "{text.lower()}"'
            data_list = sql(f'SELECT * FROM dishes WHERE title LIKE "%{text}%" LIMIT 1')


            if len(data_list) and type(data_list) == list:
                dish = InlineKeyboardButton(
                    text=title,
                    switch_inline_query_current_chat=message.text
                )
                markup.add(dish)
                message_data = {
                    'text': 'Возможно вы искали это:',
                    'reply_markup': markup,
                }
                await message.answer(**message_data)
            else:
                await message.answer('Я вас не понял.', reply_markup=InlineKeyboardMarkup().add(get_home_button()))

        await update_last_message(message, castom_message_id=message.message_id + 1)
        await message.delete()
    else:
        await update_last_message(message)
