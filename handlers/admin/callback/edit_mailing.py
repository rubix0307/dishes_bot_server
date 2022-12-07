import time
from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

from app import bot, dp
from db.functions import sql
from functions import Article, edit_preview, get_call_data, get_data_dish, get_fav_ids
from markups import mailing


@dp.callback_query_handler(mailing.filter())
async def edit_mailing(call: types.CallbackQuery, callback_data: dict()):

    user = call.from_user
    dish_id = int(callback_data['dish_id'])
    query_text = callback_data['query_text']
    add = int(callback_data['add'])


    if add:
        sql(f'INSERT INTO mailing (dish_id) VALUES ({dish_id})', commit=True)
    else:
        sql(f'DELETE FROM mailing WHERE dish_id = {dish_id}', commit=True)


    fav_ids = get_fav_ids(user.id)
    
    
    call_data = {
        'id': dish_id,
        'fav': 1 if dish_id in fav_ids else 0,
        'query': query_text,
        'num_ph': 0,
    }




    data = get_data_dish(dish_id)
    article = Article(data, callback_data=call_data, user_id=user.id)

    article, call_data = edit_preview(article, call_data)


    message_data = {
        'parse_mode': 'html',
        'reply_markup': article.get_markup(),
        'text': article.get_message_text(),
        
    }
    
    await bot.edit_message_text(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        **message_data,
    )

    
