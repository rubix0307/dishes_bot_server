import datetime

from aiogram import Bot, types
from aiogram.dispatcher import filters
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.utils.markdown import hlink

from app import bot, dp
from config import ADMIN_ID, BUY_AD_URL, MEDIA_URL
from db.functions import sql
from functions import (Article, get_data_dish, get_date, get_fav_ids,
                       update_last_message, user_activity_record, you_very_active)
from markups import get_home_button

br = '\n'
@dp.message_handler(filters.Text(contains=['get_id']), state='*')
async def show_dish(message: types.Message):

    

    user = message.from_user
    
    try:

        today_activity = sql(f'''
            SELECT COUNT(*) as `count` FROM `users_actions` 
            WHERE user_id = {user.id} AND time_at = "{get_date()}";''')
        count_activity = today_activity[0]['count']

        if count_activity >= 100:
            await you_very_active(bot, message, count_activity)
            return
    except:
        pass

    query = message.text
    text_data = query.split('&')
    dish_id = int(text_data[0].split('=')[1])

    try:
        query_text = text_data[1].split('=')[1:]
        query_text = '='.join(query_text)
    except IndexError:
        query_text = ''

    

    fav_ids = get_fav_ids(message.from_user.id)
    callback_data = {
        'id': dish_id,
        'fav': int(dish_id in fav_ids),
        'query': query_text,
        'num_ph': 0,
    }

    data = get_data_dish(dish_id)
    article = Article(data, callback_data=callback_data, user_id=user.id)
    try:
        article.preview = MEDIA_URL + data['local_photo']
    except:
        pass


    try:
        
        try:
            await message.delete()
        except MessageToDeleteNotFound:
            pass

        try:
            answer = await message.answer(reply_markup=article.get_markup(), text=article.get_message_text(), parse_mode='html')
        except ValueError as e:
            try:
                answer = await message.answer(reply_markup=article.get_markup(clear_query=True), text=article.get_message_text(), parse_mode='html')
            except Exception as e:
                print(e)

        finally:
            await update_last_message(message, castom_message_id=answer.message_id)
            
    finally:
        user_activity_record(user.id, dish_id, query)
        
        
    