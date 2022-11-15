from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from app import bot, dp
from db.functions import sql
from functions import get_home_button, get_home_page, update_last_message
from markups import call_filters, filters, show_menu


@dp.callback_query_handler(show_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):

    highlight_symbol = '⭐️ '
    menu_name = callback_data['menu_name']
    user = call.from_user

    if call_filters['home'] in menu_name:

        text = 'Главное меню'
        data = get_home_page(user.id)

        message_data = {
            'text': data['text'],
            'reply_markup': data['markup'],
            'parse_mode': 'html',
        }

        try:
            await call.message.edit_text(**message_data)
        
        except Exception as ex:
            try:
                await bot.edit_message_text(
                    inline_message_id=call.inline_message_id,
                    **message_data,
                )
            except:
                await bot.send_message(chat_id=user.id, **message_data,)
                await update_last_message(call, castom_message_id=call.message.message_id + 1)

        finally:
            await call.answer()
            return

    elif call_filters['countries'] in menu_name:
        text = 'Кухни разных стран'
        top_categories = sql(
            f'SELECT title, emoji FROM `categories` WHERE favorite = 1')
        categories = sql(
            'SELECT title, emoji FROM categories WHERE parent_id = 1 AND is_show = 1')


        new_category_list = []
        
        max_len = max([len(category['title'].split()[0]) if not category['title'].split()[0] in ['Средиземноморская','Азербайджанская'] else 0  for category in categories])
        for category in categories:
            title = category['title'].split()[0]

            spase = '⠀'* (max_len - len(title))
            category['title'] = f'''{title} {spase}{category['emoji']}'''
            new_category_list.append(category)

        for category in top_categories:
            title = category['title'].split()[0]

            spase = '⠀'* (max_len - len(title))
            category['title'] = f'''{highlight_symbol} {title} {spase[:-1]}{category["emoji"]}'''
            new_category_list.append(category)

        categories = new_category_list

    else:
        text = 'По категориям'
        categories = sql('SELECT title,emoji FROM categories WHERE parent_id = 2 AND is_show = 1')

    keyboard_markup = InlineKeyboardMarkup()
    for category in categories[:99]:

        title = category['title'].replace(highlight_symbol, '').strip().split(' ')[0][:12].lower()

        keyboard_data = {
            'text': category['title'],
            'switch_inline_query_current_chat': f'''{filters['category']}{title}''',
        }

        keyboard_markup.add(InlineKeyboardButton(**keyboard_data,))

    keyboard_markup.add(get_home_button())

    message_data = {
        'parse_mode': 'html',
        'reply_markup': keyboard_markup,
        'text': text,  
    }

    try:
        await call.message.edit_text(**message_data,)

    except:
        await bot.edit_message_text(
            inline_message_id=call.inline_message_id,
            **message_data,
        )
    await call.answer()
