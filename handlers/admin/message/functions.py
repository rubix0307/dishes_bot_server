import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.markdown import code

from app import bot, dp
from config import ADMIN_ID, BOT_URL, GROUG_ID
from db.functions import sql
from functions import update_last_message
from markups import mails_call_filter, mails_call_menu

br = '\n'
line = '—'*22

def get_action(text, action_name):
    return InlineKeyboardButton(
        text=text,
        callback_data=mails_call_menu.new(action=mails_call_filter[action_name]))

class Form(StatesGroup):
    text = State()
    photo = State()

@dp.message_handler(state='*', commands=['cancel'])
async def mailing_cancel(message: types.Message, state=FSMContext):
    await message.answer('Отменено')
    await state.finish()

@dp.callback_query_handler(lambda call: mails_call_filter['edit_text'] in call.data, state='*')
@dp.message_handler(state='*', commands=['mails'])
async def mailing_start(message: types.Message, state: FSMContext):
    text = ''
    try:
        async with state.proxy() as data:
            if data['text']:
                text = f'''Текущий текст:{br}{line}{br}{data['text']}{br}{line}{br*2}'''
    except:
        pass

    message_data = {
        'text' : f'''{text}
[Рассылка]
Для отмены /cancel

Введите текст для рассылки:
''',
        'parse_mode': 'MarkdownV2',
    }

    try:
        answer = await message.answer(**message_data)
        await message.delete()
    except:
        answer = await message.message.answer(**message_data)
        await message.message.delete()
        
    await update_last_message(message, castom_message_id = answer.message_id)
    await Form.text.set()


@dp.message_handler(state=Form.text)
async def mailing_set_text(message: types.Message, state: FSMContext):

    user_id = message.from_user.id

    async with state.proxy() as data:
        data['text'] = message.md_text
    

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(get_action('Изменить текст', 'edit_text'))
    markup.add(get_action('[dev] Изменить фото', 'edit_ph'))
    markup.add(get_action('[dev] Отправить всем', 'send_all'))

    message_data = {
        'text' : f'''Текущий текст:{br}{line}{br}{data['text']}{br}{line}{br*2}Выберите следующий пункт''',
        'reply_markup' : markup,
        'parse_mode' : 'MarkdownV2',
    }


    answer = await message.answer(**message_data)
    await Form.next()
    await message.delete()
    await update_last_message(message, castom_message_id = answer.message_id)

    



























