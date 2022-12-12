

from aiogram import types

from app import bot, dp
from config import BOT_URL
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from db.functions import sql

from markups import get_home_button

@dp.message_handler(state='*', commands=['contest'])
async def contest(message: types.Message):
    user_id = message.from_user.id
    msg = f'''
Конкурс на 50$!

Условия по кнопке ниже

Твоя ссылка:
{BOT_URL}?start={user_id}

Призы:
1 - 25$
2 - 15$
3 - 10$

ТОП 10 пригласивших:
'''
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(InlineKeyboardButton('Условия', web_app=WebAppInfo(url='https://obertivanie.com/bot_images/web-app/contest/contest.html')))
    markup.add(*[get_home_button(f'№'), get_home_button(f'участник'), get_home_button(f'''пригласил''')])

    contest_users = sql(f'''
SELECT u2.user_id as id, u2.first_name as name, COUNT(*) as count 
FROM users as u 
INNER JOIN users as u2 ON u.came_from = u2.user_id 
WHERE NOT (u.came_from REGEXP '[^0-9]') 
GROUP BY u.came_from 
ORDER BY count DESC''')

    for num, user in enumerate(contest_users):
        markup.add(*[get_home_button(f'''{f'Ты - {num + 1}' if user['id'] == user_id else num + 1 }'''), get_home_button(user['name']), get_home_button(user['count'])])

    await message.answer(msg, reply_markup=markup, disable_web_page_preview=True)