

from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.markdown import hlink, hunderline, hbold, hcode
from app import bot, dp
from config import ADMIN_ID, BOT_URL
from db.functions import sql
from functions import update_last_message, user_activity_record
from markups import call_filters, get_home_button, get_nothing_button

br = '\n'

@dp.message_handler(state='*', commands=['contest'])
async def contest(message: types.Message, is_callback=False):
    user_id = message.from_user.id
    
    

    contest_users = sql(f'''
SELECT u2.user_id as id, u2.first_name as name, COUNT(*) as count 
FROM users as u 
INNER JOIN users as u2 ON u.came_from = u2.user_id 
WHERE NOT (u.came_from REGEXP '[^0-9]') 
GROUP BY u.came_from 
ORDER BY count DESC''')

    you = {
        'pos': 0,
        'count': 0,
    }
    for num, data in enumerate(contest_users):
        if data['id'] == user_id:
            you.update({
                'pos': num +1,
                'count': data['count'],
            })

    

    msg = f'''
{hlink('Участвуйте в нашем конкурсе на призовой фонд 50 долларов! 💵', BOT_URL + '?start=contest')}

Пригласите как можно больше людей в наш бот по своей реферальной ссылке и станьте победителем 💵🍾
Конкурс проходит до Нового Года🎄

⛔️Обратите внимание, что участники, которые уже участвуют в конкурсе, или подписались по другой ссылке, не могут принять участие по вашей ссылке. Также не будут засчитываться участники, которые подписались и сразу отписались. В зачет пойдут только пользователи, подписанные на наш кулинарный бот к моменту завершения конкурса.

Призовой фонд разделится следующим образом:
1️⃣ место - 25 долларов
2️⃣ место - 15 долларов
3️⃣ место - 10 долларов

Результаты будут объявлены 31.12.2022
Способ выплаты призовых будет согласован с победителями в индивидуальном порядке для их удобства.
Удачи!

{f"📶 Ты пригласил {you['count']} человек.{br}Статистика конкурса открывается только для участников в этом же меню" if not you['pos'] else f"📶 Ты занимаешь {you['pos']} место{br}пригласил {you['count']} человек"},
    
📌 Твоя реферальная ссылка:
{BOT_URL}?start={user_id}

Быстрое приглашение друзьям:
(нажми на него что б скопировать)
{hcode(f'Мне нравится этот телеграмм бот с рецептами.{br}Советую тебе подписаться на них по моей ссылке,{br}ведь они сейчас проводят конкурс!💵{br}{BOT_URL}?start={user_id}')}


📶 ТОП 10 пригласивших:
{f'(таблица видна только участникам конкурса, т.е. успешно пригласившим хотя бы одного пользователя)' if not you['count'] else ''}


'''

    markup = InlineKeyboardMarkup(row_width=3)
    if you['pos'] or user_id == ADMIN_ID:
        if contest_users:
            markup.add(*[get_nothing_button(f'№'), get_nothing_button(f'участник'), get_nothing_button(f'''пригласил''')])

        for num, data in enumerate(contest_users[:10]):
                markup.add(*[get_nothing_button(f'''{f'- {num + 1} - ' if data['id'] == user_id else num + 1 }'''), get_nothing_button(data['name'][:20]), get_nothing_button(data['count'])])


    markup.add(get_home_button('🎄 На главную 🌟'))


    if not is_callback:
        answer = await message.answer(msg, reply_markup=markup, disable_web_page_preview=True, parse_mode='html')
        user_activity_record(user_id, None, message.text)
        await message.delete()
    else:
        answer = await bot.send_message(chat_id = user_id, text=msg, reply_markup=markup, disable_web_page_preview=True, parse_mode='html')
        user_activity_record(user_id, None, call_filters['contest'])
    await update_last_message(message, castom_message_id = answer.message_id)
   