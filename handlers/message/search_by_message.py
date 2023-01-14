
from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)

from app import bot, dp
from config import BOT_URL, MEDIA_URL
from db.functions import sql
from functions import (Article, get_data_dish, get_date,
                       get_home_button, is_edited_mode, send_categories_markup, update_last_message,
                       user_activity_record, you_very_active)
from aiogram.dispatcher import FSMContext
br = '\n'

@dp.message_handler(state='*')
async def main_def(message: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup()
    text = message.html_text
    user = message.from_user

    if not BOT_URL in text:
        if text.isdigit():
            dish_id = int(text)

            try:
                today_activity_isdigit = sql(f'''
                    SELECT COUNT(*) as `count` FROM `users_actions` 
                    WHERE `dish_id` = `query_text` AND user_id = {user.id} AND time_at = "{get_date()}";''')

                count_activity = today_activity_isdigit[0]['count']
                if count_activity >= 20 and not is_edited_mode(user.id, state):
                    await you_very_active(bot, message, count_activity)
                    return
            except:
                pass



            
            
                

            try:
                data = get_data_dish(dish_id)
            except:
                await message.answer('Я вас не понял.', reply_markup=InlineKeyboardMarkup().add(get_home_button()))

            

            
            article = Article(data, user_id=user.id)
            try:
                await message.delete()
                user_activity_record(user.id, dish_id, text)
                article.preview = MEDIA_URL + data['local_photo']
            except:
                pass
            answer = await message.answer(reply_markup=article.get_markup(), text=article.get_message_text(), parse_mode='html')
            await update_last_message(message, castom_message_id=answer.message_id)
            if is_edited_mode(user.id, state):
                async with state.proxy() as data:
                    if data['category_message_id']:
                         await bot.delete_message(chat_id=user.id, message_id=data['category_message_id'])
                    data['article_id'] = answer.message_id

                try:
                    await send_categories_markup(message=message, state=state, dishe_id=dish_id)
                except:
                    pass
            return

        elif is_edited_mode(user.id, state):

            answer_text = f'Прошла ошибка'
            try:
                category_title = text.strip('-').strip()
                category_id = sql(f'''SELECT * FROM `categories` WHERE title LIKE "%{category_title}%";''')[0]['id']
                dish_id = state.storage.data[str(user.id)][str(user.id)]['data']['dishe_id']
                category_message_id = state.storage.data[str(user.id)][str(user.id)]['data']['category_message_id']
                article_id = state.storage.data[str(user.id)][str(user.id)]['data']['article_id']
                dishes_category_ids = [data['category_id'] for data in sql(f'''SELECT * FROM `dishes_categories` WHERE dish_id = {dish_id}''')]
                
                if category_id in dishes_category_ids:
                    answer_text = f'Удалена категория "{category_title}"'
                    sql(f'''DELETE FROM `dishes_categories` WHERE `dish_id` = "{dish_id}" AND `category_id` = "{category_id}"''', commit=True)
                else:
                    answer_text = f'Добавлена категория "{category_title}"'
                    sql(f'''INSERT INTO `dishes_categories`(`dish_id`, `category_id`) VALUES ('{dish_id}','{category_id}')''', commit=True)
            except:
                answer_id = state.storage.data[str(user.id)][str(user.id)]['data']['answer_id']
                if answer_id:
                    await bot.delete_message(chat_id=user.id, message_id=answer_id)

                answer = await message.answer(answer_text)
                await message.delete()

                async with state.proxy() as data:
                    data['answer_id'] = answer.message_id

                return
                



            await bot.delete_message(chat_id=user.id, message_id=category_message_id)
            if article_id:
                await bot.delete_message(chat_id=user.id, message_id=article_id)

            data = get_data_dish(dish_id)
            article = Article(data, user_id=user.id)
            try:
                await update_last_message(message, castom_message_id=message.message_id + 1)
                user_activity_record(user.id, dish_id, text)
                article.preview = MEDIA_URL + data['local_photo']
            except:
                pass
            answer = await message.answer(reply_markup=article.get_markup(), text=article.get_message_text(), parse_mode='html')
            async with state.proxy() as data:
                data['article_id'] = answer.message_id


            answer_id = state.storage.data[str(user.id)][str(user.id)]['data']['answer_id']
            if answer_id:
                await bot.delete_message(chat_id=user.id, message_id=answer_id)

            answer = await message.answer(answer_text)
            await message.delete()

            async with state.proxy() as data:
                data['answer_id'] = answer.message_id

            
            await send_categories_markup(message=message, state=state, dishe_id=dish_id)
            return

        elif not BOT_URL in text:

            title = f'Блюдо содержит "{text.lower()}"'
            data_list = sql(f'SELECT * FROM dishes WHERE title LIKE "%{text}%" LIMIT 1')

            try:
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
            except:
                pass

        await update_last_message(message, castom_message_id=message.message_id + 1)
        await message.delete()
    else:
        await update_last_message(message)

