from textwrap import indent
from aiogram import types

from app import dp, bot
from db.functions import sql
from functions import get_home_page, register_user, update_last_message


@dp.message_handler(state='*', commands=['start'])
async def main_def(message: types.Message):
    register_user(message)

    user = message.from_user
    data = get_home_page(user.id)
    data_answer = {
        'text': data['text'],
        'reply_markup': data['markup'],
    }

    try:
        start_parameter = message.text.split()[1]
        if start_parameter == 'speed':
            data_answer.update({'text':f'''{data_answer['text']}\n\n❗️ Быстрый поиск работает только в этом чате (с ботом)'''})
        
        elif 'from=' in start_parameter:
            try:
                came_from = start_parameter.split('=')[1]
            except IndexError:
                came_from = start_parameter

            sql_query = f'''UPDATE `users` SET `came_from`='{came_from}' WHERE `user_id` = {user.id}'''
            sql(sql_query, commit=True)



    
    except IndexError:
        start_parameter = None



    
    await message.delete()
    await message.answer(**data_answer)
    await update_last_message(message, castom_message_id = message.message_id + 1)
