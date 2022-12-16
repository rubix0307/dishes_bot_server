from aiogram import types
from aiogram.types.inline_keyboard import InlineKeyboardMarkup
from app import bot, dp
from db.functions import sql
from functions import get_call_data
from markups import get_ads_stats_call_menu, get_home_button

import datetime
br = '\n'

@dp.callback_query_handler(get_ads_stats_call_menu.filter())
async def get_ads_stats(call: types.CallbackQuery, callback_data: dict()):

    date = datetime.datetime.now()
    date_today = f'{date.year}-{date.month}-{date.day}'

    l_day = date - datetime.timedelta(days=1)
    date_last_day = f'{l_day.year}-{l_day.month}-{l_day.day}'

    data_ads = sql(f'''
        SELECT u1.came_from as name, COUNT(*) as count,
        (SELECT COUNT(*) as today FROM users as u2 WHERE u2.came_from = name AND date = '{date_today}') as today,
        (SELECT COUNT(*) as today FROM users as u2 WHERE u2.came_from = name AND date = '{date_last_day}') as lastday

                
        FROM users as u1
        WHERE (u1.came_from REGEXP '[^0-9]')
        GROUP BY u1.came_from
        ORDER BY count DESC;
            ''')

    data_ads_by_user_id = sql(f'''
        SELECT u1.came_from as name, COUNT(*) as count,
        (SELECT COUNT(*) as count FROM users as u2 WHERE NOT (u2.came_from REGEXP '[^0-9]') AND date = '{date_today}') as today,
        (SELECT COUNT(*) as count FROM users as u2 WHERE NOT (u2.came_from REGEXP '[^0-9]') AND date = '{date_last_day}') as lastday        
        FROM users as u1
        WHERE NOT (u1.came_from REGEXP '[^0-9]')
        ORDER BY count DESC;''')
    
    data_ads_by_user_id[0]['name'] = 'contest'
    data_ads.append(data_ads_by_user_id[0])

    for num, f in enumerate(data_ads):
        for num2, s in enumerate(data_ads):
            if f['count'] > s['count']:
                data_ads[num], data_ads[num2] = data_ads[num2], data_ads[num]

    all_user_count = sum([d['count'] for d in data_ads])
    t_sum = sum([d['today'] for d in data_ads])
    l_sum = sum([d['lastday'] for d in data_ads])
   
    markup = InlineKeyboardMarkup(row_width=4)
    markup.add(*[
        get_home_button(f'FROM: {len(data_ads) + 1}'), 
        get_home_button(f'ALL: {all_user_count}'), 
        get_home_button(f'TDAY: {t_sum}'), 
        get_home_button(f'LDAY: {l_sum}')])

    for ad in data_ads[:50]:
        name = ad['name']
        count = ad['count']
        today = f'''+{ad['today']}''' if ad['today'] else 'ㅤ'
        lastday = f'''+{ad['lastday']}''' if ad['lastday'] else 'ㅤ'

        data = [
            get_home_button(name),
            get_home_button(count),
            get_home_button(today),
            get_home_button(lastday),
            ]

        markup.add(*data)
    

    message_data = {
        'chat_id': call.from_user.id,
        'text': f'Ads statistics',
        'message_id': call.message.message_id,
        'reply_markup': markup,
        'parse_mode': 'html',
    }

    await bot.edit_message_text(**message_data)
    await call.answer()
