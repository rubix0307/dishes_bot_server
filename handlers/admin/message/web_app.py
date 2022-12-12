from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)

from app import dp, bot
from db.functions import sql
import os
from config import GROUG_ID, MEDIA_PATH
from functions import update_last_message
number_of_file = 10
@dp.message_handler(state='*', commands=['web_app'])
async def main_def(message: types.Message):
    global number_of_file
    web_app_path = MEDIA_PATH + 'web-app/'
    web_app_files = os.listdir(web_app_path)
    for file in web_app_files:
        if '.html' in file:
            number_of_file += 1
            number = number_of_file

            name_html = web_app_path + f'{number}.html'
            os.rename(web_app_path + file, name_html)
            break

    web_app = InlineKeyboardButton(f'Сайт {name_html.split("/")[-1]}', web_app=types.WebAppInfo(url=f'https://obertivanie.com/bot_images/web-app/{name_html.split("/")[-1]}'))



    answer = await message.answer('/web_app', reply_markup=InlineKeyboardMarkup().add(web_app))
    await update_last_message(message, castom_message_id=answer.message_id)
    await message.delete()



@dp.message_handler(state='*', commands=['article'])
async def main_def(message: types.Message):
    web_app = InlineKeyboardButton(f'Читать статью', web_app=types.WebAppInfo(url=f'https://obertivanie.com/bot_images/web-app/articles/10.html'))

    await message.answer('1', reply_markup=InlineKeyboardMarkup().add(web_app))
    await bot.send_photo(
        chat_id=GROUG_ID,
        photo='https://opentv.media/wp-content/uploads/2021/12/christmas-gift-wrapping.jpg.webp',
        caption='Читайте статью\n10 вещей, которые нужно сделать до Нового года',
        disable_notification=True,
        reply_markup=InlineKeyboardMarkup().add(web_app))
                
















