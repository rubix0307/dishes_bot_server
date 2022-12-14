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

def get_stats(num, max_users, successfully, errors, start_time, is_continue=True):
    return f'''/mails_ph

Обработано: {num} / {max_users}
Успешно: {len(successfully)}
Не успешно: {len(errors)}
Потрачено времени: {round(time.time() - start_time, 0)} сек

{'Рассылка...' if is_continue else '✅ Рассылка окончена.'}
'''

@dp.message_handler(state='*', commands=['mails_ph'])
async def mails_ph(message: types.Message):
    start_time = time.time()
    all_users = sql('SELECT * FROM `users` ORDER BY `users`.`role_id` DESC')
    max_users = len(all_users)
    successfully = []
    errors = []
    admin_message = await bot.send_message(chat_id=ADMIN_ID, text='/mails_ph\nСтарт')

    for num, user in enumerate(all_users):
        if not num % 10:
            
            msg = get_stats(num, max_users, successfully, errors, start_time, is_continue=True) 
            await bot.edit_message_text(msg, chat_id=ADMIN_ID, message_id=admin_message.message_id)

        start_message = sql(f'''SELECT * FROM `start_messages` WHERE user_id = {user['user_id']}''')

        try:
            try:

                if start_message:
                    start_messages_id = start_message[0]['message_id']
                    try:
                        is_unpin = await bot.unpin_chat_message(user['user_id'], start_messages_id)
                    except:
                        pass

                    try:
                        await bot.delete_message(user['user_id'], start_messages_id)
                    except:
                        pass

                photo = await bot.send_photo(
                    chat_id=user['user_id'],
                    photo='https://obertivanie.com/bot_images/default/sub_to_group.png', 
                    reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'👩‍👦‍👦⠀В группу⠀👨‍👩‍👧', url='https://t.me/+aIOTdrZd3504NGUy')),
                    protect_content=True,
                    )
                await bot.pin_chat_message(chat_id=user['user_id'], message_id=photo.message_id)
                
                is_insert = sql(f'''INSERT INTO `start_messages`(`user_id`, `message_id`) VALUES ({user['user_id']},{photo.message_id})''', commit=True)
                if not is_insert:
                    sql(f'''UPDATE `start_messages` SET `message_id` = '{photo.message_id}' WHERE `start_messages`.`user_id` = {user['user_id']};''', commit=True)

                sql(f'''UPDATE `users` SET `is_active` = '1' WHERE `users`.`user_id` = {user['user_id']};''')
                successfully.append(user['user_id'])
            except Exception as e:
                try:
                    is_update_active = sql(f'''UPDATE `users` SET `is_active` = '0' WHERE `users`.`user_id` = {user['user_id']};''', commit=True)
                finally:
                    errors.append(user['user_id'])
        except Exception as err:
            print(errors)

    msg = get_stats(num, max_users, successfully, errors, start_time, is_continue=False)
    await bot.edit_message_text(msg, chat_id=ADMIN_ID, message_id=admin_message.message_id)