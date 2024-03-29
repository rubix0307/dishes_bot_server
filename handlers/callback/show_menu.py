from aiogram import types

from app import bot, dp
from functions.main import by_categories, by_countries, contest, get_home, groups, user_activity_record
from functions.markups import *


@dp.callback_query_handler(show_menu.filter(), state='*')
async def show_dish(call: types.CallbackQuery, callback_data: dict()):
    user = call.from_user
    try:
        menu_name = callback_data['menu_name']

        if call_filters['home'] in menu_name:
            await get_home(call)
    
        elif call_filters['categories'] in menu_name:
            await by_categories(bot, call)
        
        elif call_filters['countries'] in menu_name:
            await by_countries(bot, call)

        elif call_filters['groups'] in menu_name:
            await groups(call, is_callback=True)
        
        elif call_filters['contest'] in menu_name:
            await contest(call, is_callback=True)

        elif call_filters['nothing'] in menu_name:
            await call.answer()
            
    except:
        await get_home(call)

    finally:
        user_activity_record(user.id,'0', f'get menu {menu_name}')

    

    


   
