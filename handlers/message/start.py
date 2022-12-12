
import time
from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from app import dp, bot
from db.functions import sql
from functions import (get_home_page, register_user, update_last_message,
                       user_activity_record)


@dp.message_handler(state='*', commands=['start'])
async def main_def(message: types.Message):
    is_reg = register_user(message)

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
        
        elif 'from=' in start_parameter or start_parameter.isdigit():
            try:
                came_from = start_parameter.split('=')[1]
            except IndexError:
                came_from = start_parameter

            sql_query = f'''UPDATE `users` SET `came_from`='{came_from}' WHERE `user_id` = {user.id}'''
            sql(sql_query, commit=True)



    
    except IndexError:
        start_parameter = None



    
    
    finally:
        is_start_photo = bool(sql(f'''SELECT COUNT(*) as count FROM `start_messages` WHERE user_id = {user.id}''')[0]['count'])
        if is_reg or not is_start_photo:
            try:
                photo = await message.answer_photo(photo='https://obertivanie.com/bot_images/default/panda_sub.png', protect_content=True,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'👩‍👦‍👦⠀В группу⠀👨‍👩‍👧', url='https://t.me/+aIOTdrZd3504NGUy')))
                time.sleep(0.2)
                await bot.pin_chat_message(chat_id=user.id, message_id=photo.message_id)
                sql(f'''INSERT INTO `start_messages`(`user_id`, `message_id`) VALUES ({user.id},{photo.message_id})''')
            except:
                pass

        answer = await message.answer(**data_answer)
        await update_last_message(message, castom_message_id = answer.message_id)
        user_activity_record(user.id, None, message.text)
        await message.delete()