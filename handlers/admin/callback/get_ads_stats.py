from aiogram import types
from aiogram.types.inline_keyboard import InlineKeyboardMarkup
from app import bot, dp
from db.functions import sql
from functions import get_call_data
from markups import get_ads_stats_call_menu, get_home_button
br = '\n'

@dp.callback_query_handler(get_ads_stats_call_menu.filter())
async def get_ads_stats(call: types.CallbackQuery, callback_data: dict()):

    all_user_count = sql(f'''SELECT COUNT(*) as count 
            FROM users''')[0]['count']
    data_ads = sql(f'''
            SELECT came_from as name, COUNT(*) as count 
            FROM users
            GROUP BY came_from
            ORDER BY count DESC;
            ''')
    

    markup = InlineKeyboardMarkup(row_width=2)

    for ad in data_ads[:50]:
        name_ad = ad['name']
        count = ad['count']
        markup.add(get_home_button(name_ad), get_home_button(count))
    
    message_data = {
        'text': f'Всего: {all_user_count}{br*2}От куда / количество',
        'reply_markup': markup,
        'parse_mode': 'html',
    }


    await bot.edit_message_text(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        **message_data,
    )

    await call.answer()
