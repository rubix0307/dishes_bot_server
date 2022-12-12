


import datetime
import time
from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from config import ADMIN_ID, BOT_URL, GROUG_ID
from db.functions import sql
from app import bot, dp
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound, BotBlocked
from aiogram.utils.markdown import hlink
from markups import get_home_button
br = '\n'

@dp.message_handler(state='*', commands=['del_messages_and_sub_panda'])
async def dell_messages(message: types.Message):
    all_users = sql('SELECT * FROM `users` ORDER BY `users`.`role_id` DESC')

    now = datetime.datetime.now()
    date = f'{now.year}-{now.month}-{now.day}'

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton('👩‍👦‍👦 Перейти в групу 🆕', url='https://t.me/+iLKIrQAhfy9kZjUy'))

    users = 0
    all_steps = 0
    blocked = 0
    errors = 0

    for user in all_users:
        users += 1
        print(users)
        try:
            try:
                user_id = user['user_id']
                if user_id == 782790707:
                    continue

                send_photo_data = await bot.send_photo(
                    chat_id=user_id,
                    photo='https://obertivanie.com/bot_images/default/panda_sub.png',
                    caption=f'''Посмотри новые посты в нашей группе{br*2}Открыть главное меню бота - /start''',
                    reply_markup=markup,
                    protect_content=True,
                    parse_mode='html',
                    )
                last_message_id = send_photo_data.message_id
                is_update = sql(f'''INSERT INTO mailing_user(user_id, date, message_id) VALUES ({user_id},'{date}',{last_message_id})''', commit=True)
                if not is_update:
                    sql(f'''UPDATE mailing_user SET user_id={user_id},date='{date}',message_id={last_message_id} WHERE 1''', commit=True)


                deleted = 0
                exceptions = 0
                for id in range(last_message_id-1, 0, -1):
                    try:
                        await bot.delete_message(
                            chat_id=user_id,
                            message_id=id
                        )
                        time.sleep(0.1)
                        deleted += 1
                    except Exception as ex:
                        if deleted:
                            exceptions += 1

                        if exceptions > 100:
                            break
                        continue
                time.sleep(0.3)
                all_steps += 1
            except BotBlocked:
                blocked += 1
                sql(f'''UPDATE `users` SET `is_active` = '0' WHERE `users`.`user_id` ={user_id};''', commit=True)
        except Exception as e:
            errors += 1
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f'''Рассылка
Всего: {users}
Успешны: {all_steps}
Заблокированы: {blocked}
Ошибки: {errors}
        '''
    )































