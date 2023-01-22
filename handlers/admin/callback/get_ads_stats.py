import random
from aiogram import types
from aiogram.types.inline_keyboard import InlineKeyboardMarkup
from app import bot, dp
from config import DEBUG
from functions import db
from functions.admin import StatsTableHtml, format_string
from functions.markups import get_home_button, get_ads_stats_call_menu
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.types.web_app_info import WebAppInfo
import datetime
br = '\n'


@dp.callback_query_handler(get_ads_stats_call_menu.filter())
async def get_ads_stats(call: types.CallbackQuery, callback_data: dict()):

    days = []
    date = datetime.datetime.now()
    for i in range(3):
        l_day = date - datetime.timedelta(days=i)
        days.append(f'{l_day.year}-{l_day.month}-{l_day.day}')

    data_ads = []
    for i in range(2):
        rules = [
            "u.came_from = name" if i else "NOT (u.came_from REGEXP '[^0-9]')",
            '' if i else "NOT",
            "GROUP BY u1.came_from" if i else "",
        ]

        answer = db.sql(f'''
            SELECT u1.came_from as name, COUNT(*) as count,
            (SELECT COUNT(*) FROM users as u WHERE u.came_from = name AND u.is_active = 0) as noactive,
            (SELECT COUNT(*) FROM users as u WHERE {rules[0]} AND date(`date`) = '{days[0]}') as today,
            (SELECT COUNT(*) FROM users as u WHERE {rules[0]} AND date(`date`) = '{days[0]}' AND u.is_active = 0) as today_noactive,
            (SELECT COUNT(*) FROM users as u WHERE {rules[0]} AND date(`date`) = '{days[1]}') as lastday,
            (SELECT COUNT(*) FROM users as u WHERE {rules[0]} AND date(`date`) = '{days[1]}' AND u.is_active = 0) as lastday_noactive,
            (SELECT COUNT(*) FROM users as u WHERE {rules[0]} AND date(`date`) = '{days[2]}') as day_before_yesterday,
            (SELECT COUNT(*) FROM users as u WHERE {rules[0]} AND date(`date`) = '{days[2]}' AND u.is_active = 0) as day_before_yesterday_noactive
            
            FROM users as u1
            WHERE {rules[1]} (u1.came_from REGEXP '[^0-9]')
            {rules[2]}
            ORDER BY count DESC;
        ''')

        if not i:
            answer[0]['name'] = 'contest'
        data_ads.append(answer)

    ads = data_ads[0] + data_ads[1]
    ads = sorted(ads, key=lambda x: x['count']-x['noactive'], reverse=True)


    count_campaigns = len(ads)
    count_all = sum([i['count'] for i in ads])
    count_all_noactive = sum([i['noactive'] for i in ads])

    count_today = sum([i['today'] for i in ads])
    count_today_noactive = sum([i['today_noactive'] for i in ads])

    count_lastday = sum([i['lastday'] for i in ads])
    count_lastday_noactive = sum([i['lastday_noactive'] for i in ads])

    count_day_before_yesterday = sum([i['day_before_yesterday'] for i in ads])
    count_day_before_yesterday_noactive = sum([i['day_before_yesterday_noactive'] for i in ads])


    table = StatsTableHtml()
    table.create_header(
        count_campaigns,
        count_all-count_all_noactive,
        count_all_noactive,
        count_today-count_today_noactive,
        count_today_noactive,
        count_lastday-count_lastday_noactive,
        count_lastday_noactive,
        count_day_before_yesterday-count_day_before_yesterday_noactive,
        count_day_before_yesterday_noactive,
    )

    markup = InlineKeyboardMarkup(row_width=5)
    markup.add(*[
        get_home_button(f'name: {count_campaigns}'),
        get_home_button(f'{count_all-count_all_noactive} (-{count_all_noactive})'),
        get_home_button(f'T: {count_today-count_today_noactive} (-{count_today_noactive})'),
        get_home_button(f'L: {count_lastday-count_lastday_noactive} (-{count_lastday_noactive})'),
        get_home_button(f'BY: {count_day_before_yesterday-count_day_before_yesterday_noactive} (-{count_day_before_yesterday_noactive})'),
        ])

    
    for num, ad in enumerate(ads):
        if num < 18:
            name = ad['name']
            count = format_string(ad['count'], ad['noactive'])
            td = format_string(ad['today'], ad['today_noactive'])
            ld = format_string(ad['lastday'], ad['lastday_noactive'])
            dby = format_string(ad['day_before_yesterday'], ad['day_before_yesterday_noactive'])
            
            data = [
                get_home_button(name),
                get_home_button(count),
                get_home_button(td),
                get_home_button(ld),
                get_home_button(dby),
            ]
            markup.add(*data)
        table.add_row(is_white= num % 2, **ad)
    if not DEBUG:
        forder = '/var/www/admin/www/obertivanie.com/bot_images/ads/'
        stats_file_name = f'stats_ads{random.randint(0,10)}.html'
        table.save_page(style_path=forder + 'table1.css', path=forder + stats_file_name)
        markup.add(InlineKeyboardButton('Полная статистика', web_app=WebAppInfo(url=f'https://obertivanie.com/bot_images/ads/{stats_file_name}')))
    
    message_data = {
        'chat_id': call.from_user.id,
        'text': f'Ads statistics',
        'message_id': call.message.message_id,
        'reply_markup': markup,
        'parse_mode': 'html',
    }

    await bot.edit_message_text(**message_data)
    await call.answer()
