
import time
from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from app import dp, bot
from db.functions import sql
from functions import (get_home_page, register_user, update_last_message,
                       user_activity_record)
from handlers.message.contest import contest
from markups import call_filters
br = '\n'
@dp.message_handler(state='*', commands=['start'])
async def main_def(message: types.Message):
    is_reg = register_user(message)

    user = message.from_user
    

    btn_title = None
    btn_search = None
    add_title_row = None

    data_answer = {
        'text': '',
    }
    

    try:
        is_return = False
        start_parameters = message.text.split()[1].split('__')

        for start_parameter in start_parameters:
            if start_parameter == 'speed':
                data_answer.update({'text':f'''{data_answer['text']}{br*2}❗️ Быстрый поиск работает только в этом чате (с ботом)'''})
            
            elif 'from=' in start_parameter or start_parameter.isdigit():

                try:
                    came_from = start_parameter.split('=')[1]
                except IndexError:
                    came_from = start_parameter

                last_from = sql(f'''SELECT came_from FROM `users` WHERE user_id = {user.id}''')[0]

                if last_from['came_from'] == came_from:
                    data_answer.update({'text':f'''{data_answer['text']}{br*2}❗️ Вы уже были приглашены этим пользователем'''})
                    continue

                elif last_from['came_from'] and last_from['came_from'].isdigit() and came_from.isdigit():
                    data_answer.update({'text':f'''{data_answer['text']}{br*2}❗️ Вы уже были приглашены другим пользователем'''})
                    continue

                elif came_from == str(user.id):
                    data_answer.update({'text':f'''{data_answer['text']}{br*2}❗️ Вы не можете пригласить сами себя'''})
                    continue

                try:
                    if not last_from['came_from'] or not last_from['came_from'].isdigit():
                        sql_query = f'''UPDATE `users` SET `came_from`='{came_from}' WHERE `user_id` = {user.id}'''
                        sql(sql_query, commit=True)
                        continue
                except Exception as e:
                    pass

            elif start_parameter == call_filters['contest']:
                await contest(message)
                await update_last_message(message, castom_message_id = message.message_id + 1)
                user_activity_record(user.id, None, message.text)

                is_return = True

            elif 'gcategory=' in start_parameter:
                cat = start_parameter.split('=')[1]
                categories = {
                    'zavtrak':['🍳 ЗАВТРАК', 'Категория=завтраки', 'свой '],
                    'pervie':['🍲 ПЕРВЫЕ БЛЮДА', 'Категория=супы', 'вкуснейшие '],
                    'osnovnie':['🍖 ОСНОВНЫЕ БЛЮДА', 'Категория=основные', ''],
                    'obed':['🍽 НА ОБЕД', 'Категория=основные', 'что покушать '],
                    'desert':['🥞 ДЕСЕРТЫ', 'Категория=выпечка', 'невероятные '],
                }
                if cat in categories.keys():
                    btn_title = categories[cat][0] + ' 👩‍🍳'
                    btn_search = categories[cat][1]
                    add_title_row = f'Смотри {categories[cat][2]} {categories[cat][0]} по кнопке ниже'
                

    
    except IndexError:
        start_parameter = None

    if is_return:
        return

    data = get_home_page(user.id, btn_title=btn_title, btn_search=btn_search, add_title_row=add_title_row)
    data_answer = {
        'text': f'''{data['text']} {data_answer['text']}''',
        'reply_markup': data['markup'],
    }
    

    try:
        is_start_photo = bool(sql(f'''SELECT COUNT(*) as count FROM `start_messages` WHERE user_id = {user.id}''')[0]['count'])
        if is_reg or not is_start_photo:
                photo = await message.answer_photo(photo='https://obertivanie.com/bot_images/default/sub_to_group.png', protect_content=True,
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