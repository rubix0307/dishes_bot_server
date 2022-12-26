import datetime
import time
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from db.functions import sql

from functions import get_user_role, update_last_message
from markups import mails_call_filter, mails_call_menu
from app import bot
br = '\n'
line = '—'*22
mailing_cancel_data = 'Для отмены рассылки — /cancel'

class Form(StatesGroup):
    text = State()
    photo = State()
    disable_web_page_preview = False

def get_action(text, action_name):
    return InlineKeyboardButton(
        text=text,
        callback_data=mails_call_menu.new(action=mails_call_filter[action_name]))

async def set_default_data_mails(data):
    if not 'disable_web_page_preview' in data.keys():
        data['disable_web_page_preview'] = False
    if not 'paddings_state' in data.keys():
        data['paddings_state'] = False

async def send_or_edit_message(message, message_data):
        try:
            try:
                answer = await message.message.edit_text(**message_data)
            except:
                answer = await message.message.answer(**message_data)
                await message.message.delete()
        except:
            answer = await message.answer(**message_data)
            await message.delete()
        return answer

async def mailing_cancel(message: types.Message, state=FSMContext):
    message_data = {
        'text': 'Рассылка отменена',
    }
    await send_or_edit_message(message, message_data)
    await state.finish()


async def mailing_start(message, state):
        text = ''
        message_data = {}
        try:
            async with state.proxy() as data:
                await set_default_data_mails(data)

                if data['text']:
                    text = f'''Текущий текст:{br}{line}{br}{data['text']}'''
                    markup = InlineKeyboardMarkup(row_width=1)
                    markup.add(get_action('[mail] К настройкам', 'settings'))
                    message_data.update({'reply_markup': markup})
                
        except:
            pass

        message_data.update ({
            'text' : f'''
[Рассылка]
{mailing_cancel_data}
Введите текст для рассылки:


{text}
''',
            'parse_mode': 'MarkdownV2',
            'disable_web_page_preview' : data['disable_web_page_preview'],
        })

        answer = await send_or_edit_message(message, message_data)
            
        await update_last_message(message, castom_message_id = answer.message_id)
        await Form.text.set()


async def get_preview_mail(message: types.Message, data):
    await set_default_data_mails(data)

    web_page_preview_state = f'''Предпоказ: {'✅' if not data['disable_web_page_preview'] else '❌'}'''
    paddings_state = f'''Отступ: {'✅' if data['paddings_state'] else '❌'}'''

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(get_action('Изменить текст', 'edit_text'))

    try:
        if 'http' in message.message.html_text:
            markup.add(get_action(web_page_preview_state, 'preview_state'))
    except:
        if 'http' in message.html_text:
            markup.add(get_action(web_page_preview_state, 'preview_state'))


    markup.add(get_action(paddings_state, 'paddings_state'))
    markup.add(get_action('Отправить себе', 'self_send'))
    markup.add(get_action('[dev] Отправить всем', 'send_all'))

    message_data = {
        'text' : f'''{mailing_cancel_data}{br*2}Текущий текст:{br}{line}{br}{data['text']}''',
        'reply_markup' : markup,
        'parse_mode' : 'MarkdownV2',
        'disable_web_page_preview': data['disable_web_page_preview'],
    }

    answer = await send_or_edit_message(message, message_data)
    
    await Form.next()
    await update_last_message(message, castom_message_id = answer.message_id)

async def mailing_set_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    async with state.proxy() as data:
        data['text'] = message.md_text
        await get_preview_mail(message=message, data=data)
    

    
async def edit_preview_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['disable_web_page_preview'] = not data['disable_web_page_preview']
        await get_preview_mail(message=message, data=data)


async def edit_paddings_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await set_default_data_mails(data)
        data['paddings_state'] = not data['paddings_state']

        if data['paddings_state']:
            data['text'] = f'''ㅤ{br}{data['text']}{br}ㅤ'''
        else:
            data['text'] = data['text'].strip(f'ㅤ{br}').strip(f'{br}ㅤ')

        await get_preview_mail(message=message, data=data)







async def send_stats_curr_mail(chat_id, mails, errors, message_data, num, max_users,edit=True, message_id=None):
    data = {
        'chat_id': chat_id,
        'text': f'''Рассылка {num+1}/{max_users}{br}Отправлено: {mails}{br}Не отправлено: {errors}{br*2}Сообщение рассылки:{br}{line}{br}{message_data['text']}''',
        'disable_web_page_preview': message_data['disable_web_page_preview'],
        'parse_mode': message_data['parse_mode'],
    }
    try:
        if edit:
            return await bot.edit_message_text(**data, message_id=message_id)
        else:
            return await bot.send_message(**data)
    except:
        pass


async def send_mailing(message, state: FSMContext, only_me=True):
    try:
        chat_id = message.from_user.id
        role = get_user_role(chat_id)
        async with state.proxy() as data:
            message_data = {
                'text' : data['text'],
                'disable_web_page_preview': data['disable_web_page_preview'],
                'parse_mode' : 'MarkdownV2',
            }

        if only_me:
            answer = await bot.send_message(chat_id=chat_id, **message_data)
            await message.answer()
            time.sleep(5)
            await bot.delete_message(chat_id=chat_id, message_id=answer.message_id)

        elif role in [2,3] and not only_me:
            all_users = sql(f'''SELECT * FROM `users` ORDER BY `users`.`role_id` DESC''')
            max_users = len(all_users)
            now = datetime.datetime.now()
            date = f'{now.year}-{now.month}-{now.day}'
            
            mails = 0
            errors = 0

            

            stats_message = await send_stats_curr_mail(chat_id, mails, errors, message_data, 0, max_users, edit=False)
            await message.message.delete()
            await state.finish()
            for num, data in enumerate(all_users):

                if not num % 10:
                    await send_stats_curr_mail(chat_id, mails, errors, message_data, num, max_users, message_id=stats_message.message_id)


                user_id = data['user_id']
                try:
                    answer = await bot.send_message(chat_id=user_id, **message_data)
                    sql(f'''UPDATE `users` SET `is_active` = '1' WHERE `users`.`user_id` = {user_id};''', commit=True)
                    is_insert = sql(f'''INSERT INTO `mailing_user`(user_id, date, message_id) VALUES ({user_id},'{date}', {answer.message_id})''', commit=True)

                    mails += 1
                except:
                    sql(f'''UPDATE users SET is_active = '0' WHERE user_id = {user_id};''', commit=True)
                    errors += 1
                    continue


            await send_stats_curr_mail(chat_id, mails, errors, message_data, num, max_users, message_id=stats_message.message_id)

    except:
        pass

































