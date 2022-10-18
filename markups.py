import copy

from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.callback_data import CallbackData

br = '\n'

mailing = CallbackData('add_mailing', 'dish_id', 'add', 'query_text')
show_menu = CallbackData('show_menu', 'menu_name')
base_markup_menu = CallbackData('base_markup_menu',
    'id',
    'fav',
    'query',
    'num_ph'
    )

get_by_id_call_menu = copy.deepcopy(base_markup_menu)
get_by_id_call_menu.prefix = 'get_dish'

edit_fav_by_id_call_menu = copy.deepcopy(base_markup_menu)
edit_fav_by_id_call_menu.prefix = 'edit_fav'


set_photo_call_menu = copy.deepcopy(base_markup_menu)
set_photo_call_menu.prefix = 'set_ph'




filters = {
    'favorites': 'избранное',
    'top-day': 'top-day',
    'category': 'Категория=',
    'mailing': 'mailing',
}

call_filters = {
    'home': 'home',
    'countries': 'countries',
    'categories': 'categories',

}


# inline buttons
def get_home_button(text: str = '⭕️ Главная страница ⭕️'):
    return InlineKeyboardButton(
        text=text,
        callback_data=show_menu.new(menu_name=call_filters['home'])
    )


def get_back_to_inline(button_text: str = f'↪️ Назад', query_text: str = ''):
    return InlineKeyboardButton(
        text=button_text,
        switch_inline_query_current_chat=query_text,
    )
