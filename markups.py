import copy

from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.callback_data import CallbackData

br = '\n'

mailing = CallbackData('add_mailing', 'dish_id', 'add', 'query_text')
mail_now = CallbackData('mail_now', 'dish_id')

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
    'mailing': 'рассылка в группу',
}

call_filters = {
    'home': 'home',
    'countries': 'countries',
    'categories': 'categories',
    'contest': 'contest',
    'nothing': 'nothing',
    'groups': 'groups',
}


# inline buttons
def get_home_button(text: str = '⭕️ Главная страница ⭕️'):
    return InlineKeyboardButton(
        text=text,
        callback_data=show_menu.new(menu_name=call_filters['home'])
    )

def get_nothing_button(text: str = 'Ничего'):
    return InlineKeyboardButton(
        text=text,
        callback_data=show_menu.new(menu_name=call_filters['nothing'])
    )


def get_back_to_inline(button_text: str = f'↪️ Назад', query_text: str = ''):
    return InlineKeyboardButton(
        text=button_text,
        switch_inline_query_current_chat=query_text,
    )






# admin

get_ads_stats_call_menu = CallbackData('get_ads')

mails_call_filter = {
    'edit_text': 'edit_text',
    'edit_ph': 'edit_ph',
    'send_all': 'send_all',
    'preview_state': 'preview_state',
    'paddings_state': 'paddings_state',
    'share_state': 'share_state',
    'protect_content_state': 'protect_content_state',
    'self_send': 'self_send',
    'send_all': 'send_all',
    'settings': 'settings',
}

mails_call_menu = CallbackData('mails', 'action')