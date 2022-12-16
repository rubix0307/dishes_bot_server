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

    

    all_user_count = sql(f'''SELECT COUNT(*) as count 
            FROM users''')[0]['count']
    data_ads = sql(f'''
            SELECT came_from as name, COUNT(*) as count 
            FROM users
            WHERE (came_from REGEXP '[^0-9]')
            GROUP BY came_from
            ORDER BY count DESC
            ''')

    date = datetime.datetime.now()
    date_today = f'{date.year}-{date.month}-{date.day}'
    data_ads_today = sql(f'''SELECT came_from as name , COUNT(*) as count 
            FROM users 
            WHERE date = '{date_today}' 
            GROUP BY came_from;''')

    l_day = date - datetime.timedelta(days=1)
    date_last_day = f'{l_day.year}-{l_day.month}-{l_day.day}'
    data_ads_l_day = sql(f'''SELECT came_from as name , COUNT(*) as count 
            FROM users 
            WHERE date = '{date_last_day}' 
            GROUP BY came_from;''')

    
    today_sum = sum([td['count'] for td in data_ads_today])
    l_sum = sum([td['count'] for td in data_ads_l_day])
    markup = InlineKeyboardMarkup(row_width=4)
    markup.add(*[get_home_button(f'FROM: {len(data_ads) + 1}'), get_home_button(f'ALL: {all_user_count}'), get_home_button(f'TODAY: {today_sum}'), get_home_button(f'LAST DAY: {l_sum}')])

    for ad in data_ads[:50]:
        name_ad = ad['name']
        count = ad['count']
        data = [get_home_button(name_ad), get_home_button(count)]

        for today in data_ads_today:
            name_ad_today = today['name']
            count_today = today['count']
            if name_ad == name_ad_today and count_today:
                data.append(get_home_button(f'+{count_today}'))
                break
        if len(data) == 2:
            data.append(get_home_button(f'⠀'))

        for l_day in data_ads_l_day:
            name_ad_l_day = l_day['name']
            count_l_day = l_day['count']
            if name_ad == name_ad_l_day and count_l_day:
                data.append(get_home_button(f'+{count_l_day}'))
                break
        if len(data) == 3:
            data.append(get_home_button(f'⠀'))

        markup.add(*data)
    


    all_self_user = sql(f'''SELECT COUNT(*) as count 
            FROM users
            WHERE NOT (came_from REGEXP '[^0-9]')
            ''')[0]['count']

    data_ads_today = sql(f'''SELECT COUNT(*) as count 
            FROM users 
            WHERE date = '{date_today}' AND NOT (came_from REGEXP '[^0-9]')''')

    data_ads_last_day = sql(f'''SELECT COUNT(*) as count 
            FROM users 
            WHERE date = '{date_last_day}' AND NOT (came_from REGEXP '[^0-9]')''')
        
    markup.add(*[get_home_button('contest'),
        get_home_button(f'{all_self_user}'),
        get_home_button(f'''+{data_ads_today[0]['count']}'''),
        get_home_button(f'''+{data_ads_last_day[0]['count']}''')
    ])

    message_data = {
        'text': f'Ads statistics',
        'reply_markup': markup,
        'parse_mode': 'html',
    }


    await bot.edit_message_text(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        **message_data,
    )

    await call.answer()
