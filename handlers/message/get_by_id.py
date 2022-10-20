from aiogram import types
from aiogram.dispatcher import filters
from aiogram.utils.exceptions import MessageToDeleteNotFound

from app import dp
from config import MEDIA_URL
from db.functions import sql
from functions import Article, get_data_dish, get_fav_ids, update_last_message, user_activity_record


@dp.message_handler(filters.Text(contains=['get_id']))
async def show_dish(message: types.Message):

    try:
        await message.delete()
    except MessageToDeleteNotFound:
        pass

    user = message.from_user
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
        await update_last_message(message, castom_message_id=message.message_id + 1)
        await message.answer(reply_markup=article.get_markup(), text=article.get_message_text(), parse_mode='html')
    
    finally:
        user_activity_record(user.id, dish_id, query_text)
    