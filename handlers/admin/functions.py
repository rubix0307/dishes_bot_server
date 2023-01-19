import datetime
import time
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from config import DEBUG, GROUG_ID
from db.functions import sql
from aiogram.utils.markdown import hlink
from aiogram.utils.exceptions import MessageCantBeForwarded
from functions import get_home_page, get_user_role, update_last_message
from markups import mails_call_filter, mails_call_menu
from app import bot
br = '\n'
line = '—'*22
mailing_cancel_data = 'Для отмены рассылки — /cancel'
default_text = 'Текст не указан ⭕️'
class Form(StatesGroup):
    text = State()
    photo = State()
    disable_web_page_preview = False
    share_state = False

def get_action(text, action_name):
    return InlineKeyboardButton(
        text=text,
        callback_data=mails_call_menu.new(action=mails_call_filter[action_name]))

async def set_default_data_mails(data):
    if not 'disable_web_page_preview' in data.keys():
        data['disable_web_page_preview'] = False

    if not 'disable_web_page_preview' in data.keys():
        data['disable_web_page_preview'] = False

    if not 'paddings_state' in data.keys():
        data['paddings_state'] = False

    if not 'text' in data.keys():
        data['text'] = default_text

    if not 'share_state' in data.keys() or data['text'].isdigit():
        data['share_state'] = data['text'].isdigit()

    if not 'protect_content' in data.keys():
        data['protect_content'] = False

    if not 'self_view' in data.keys():
        data['self_view'] = False

        


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
                data['self_view'] = False

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
Введите текст для рассылки или id сообщения для перессылки:


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
    share_state = f'''Пересылка сообщения: {'✅' if data['share_state'] else '❌'}'''
    protect_content_state = f'''Копирование: {'✅' if not data['protect_content'] else '❌'}'''

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(get_action('Изменить текст', 'edit_text'))

    if not data['share_state']:
        try:
            if 'http' in message.message.html_text:
                markup.add(get_action(web_page_preview_state, 'preview_state'))
        except:
            if 'http' in message.html_text:
                markup.add(get_action(web_page_preview_state, 'preview_state'))
        markup.add(get_action(paddings_state, 'paddings_state'))
    else:
        markup.add(get_action(protect_content_state, 'protect_content_state'))

    if data['text'].isdigit():
        markup.add(get_action(share_state, 'share_state'))


        
    markup.add(get_action('Отправить себе', 'self_send'))
    if data['self_view']:
        markup.add(get_action('Отправить всем', 'send_all'))

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

        if data['text'] == default_text:
            return await message.answer('Укажите тектс для рассылки')

        data['paddings_state'] = not data['paddings_state']

        if data['paddings_state']:
            data['text'] = f'''ㅤ{br}{data['text']}{br}ㅤ'''
        else:
            data['text'] = data['text'].strip(f'ㅤ{br}').strip(f'{br}ㅤ')

        await get_preview_mail(message=message, data=data)


async def edit_share_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await set_default_data_mails(data)

        data['share_state'] = False
        data['text'] = default_text

        await get_preview_mail(message=message, data=data)


async def edit_protect_content_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await set_default_data_mails(data)
        data['protect_content'] = not data['protect_content']

        await get_preview_mail(message=message, data=data)







async def send_stats_curr_mail(chat_id, mails, errors, message_data, num, max_users,edit=True, message_id=None, is_share = False, data_text=''):
    if not is_share:
        data = {
            'chat_id': chat_id,
            'text': f'''Рассылка {num+1}/{max_users}{br}Отправлено: {mails}{br}Не отправлено: {errors}{br*2}Сообщение рассылки:{br}{line}{br}{message_data['text']}''',
            'disable_web_page_preview': message_data['disable_web_page_preview'],
            'parse_mode': message_data['parse_mode'],
        }
    else:
        data = {
            'chat_id': chat_id,
            'text': f'''Рассылка {num+1}/{max_users}{br}Отправлено: {mails}{br}Не отправлено: {errors}{br*2}Пересылается сообщение {hlink(f'№{data_text}', f'https://t.me/best_recipe_group/{data_text}')} с группы''',
            'parse_mode': 'html',
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
            if data['text'] == default_text:
                await message.answer('Укажите текст для рассылки')
                return

            share_state = data['share_state']
            data_text = data['text']

            if not share_state:
                mail_function = bot.send_message
                message_data = {
                    'text' : data['text'],
                    'disable_web_page_preview': data['disable_web_page_preview'],
                    'parse_mode' : 'MarkdownV2',
                }
            else:
                mail_function = bot.forward_message
                message_data = {
                    'from_chat_id': GROUG_ID,
                    'message_id' : data['text'].split('/')[-1],
                    'protect_content' : data['protect_content'],
                }

        if only_me:
            try:
                answer = await mail_function(chat_id=chat_id, **message_data)
            except MessageCantBeForwarded:
                return await message.answer('нельзя переслать сообщение')
            await message.answer()
            time.sleep(5)
            await bot.delete_message(chat_id=chat_id, message_id=answer.message_id)
            async with state.proxy() as data:
                data['self_view'] = True
                await get_preview_mail(message, data)
            await message.delete()
            

        elif role in [2,3] and not only_me:
            all_users = sql(f'''SELECT * FROM `users` ORDER BY `users`.`role_id` DESC''')
            max_users = len(all_users)
            now = datetime.datetime.now()
            date = f'{now.year}-{now.month}-{now.day}'
            
            mails = 0
            errors = 0

            

            stats_message = await send_stats_curr_mail(chat_id, mails, errors, message_data, 0, max_users, edit=False, is_share=share_state, data_text=data_text)


            try:
                await message.message.delete()
            except:
                pass
            await state.finish()
            for num, data in enumerate(all_users):

                if not num % 10:
                    await send_stats_curr_mail(chat_id, mails, errors, message_data, num, max_users, message_id=stats_message.message_id, is_share=share_state, data_text=data_text)


                user_id = data['user_id']
                try:
                    answer = await mail_function(chat_id=user_id, **message_data)
                    sql(f'''UPDATE `users` SET `is_active` = '1' WHERE `users`.`user_id` = {user_id};''', commit=True)
                    is_insert = sql(f'''INSERT INTO `mailing_user`(user_id, date, message_id) VALUES ({user_id},'{date}', {answer.message_id})''', commit=True)

                    mails += 1
                except:
                    sql(f'''UPDATE users SET is_active = '0' WHERE user_id = {user_id};''', commit=True)
                    errors += 1
                    continue


            await send_stats_curr_mail(chat_id, mails, errors, message_data, num, max_users, message_id=stats_message.message_id, is_share=share_state, data_text=data_text)

    except Exception as ex:

        pass





class EditCategories(StatesGroup):
    active = State()


async def edit_categories_cancel(message: types.Message, state=FSMContext):
    user_id = message.from_user.id


    async with state.proxy() as data:
        answer_id = data['answer_id']
        article_id = data['article_id']
        start_msg_id = data['message_id']
        category_message_id = data['category_message_id']


    message_data = get_home_page(user_id)
    message_data = {
        'text': message_data['text'],
        'reply_markup': message_data['markup'],
    }
    answer = await message.answer(**message_data)
    await message.delete()
    await update_last_message(message, castom_message_id=answer.message_id)
    for id in [answer_id, start_msg_id, category_message_id, article_id]:
        if id:
            try:
                await bot.delete_message(chat_id=user_id, message_id=id)
            except:
                pass
    await state.finish()


async def edit_categories(message: types.Message, state=FSMContext):
    answer = await message.answer(f'''
Вы сейчас в режиме редактирования
Возможности:
- в карточке блюда изменить категории


Для выхода с режима - /stop

''')
    await EditCategories.active.set()
    async with state.proxy() as data:
        data['message_id'] = answer.message_id
        data['answer_id'] = None
        data['article_id'] = None
        data['category_message_id'] = None
    await message.delete()









def format_string(day, noactive):
    if day:
        return f"{day-noactive if day  else 'ㅤ'} {f'(-{noactive})' if noactive else ''}"
    else:
        return 'ㅤ'







class StatsTableHtml:
    def __init__(self):
        self.rows = []
        
    def create_header(self,count_campaigns, count:int, count_min:int, t_count:int, t_min:int, yesterday:int, yesterday_min:int, before:int, before_min:int):
        self.header = f'''
<tr>
    <th>{count_campaigns}</th>
    <th>{count if count else ''}{f'<br>-{count_min}' if count_min else ''}</th>
    <th>{t_count if t_count else ''}{f'<br>-{t_min}' if t_min else ''}</th>
    <th>{yesterday if yesterday else ''}{f'<br>-{yesterday_min}' if yesterday_min else ''}</th>
    <th>{before if before else ''}{f'<br>-{before_min}' if before_min else ''}</th>
</tr>
'''


    def add_row(self, name:str, count:int, noactive:int, today:int, today_noactive:int, lastday:int, lastday_noactive:int, day_before_yesterday:int, day_before_yesterday_noactive:int, is_white: bool = False) -> None:
        self.rows.append(f'''<tr {'class="white"' if not is_white else ''}>
<td>{name}</td>
<td>{count-noactive}{f'<br>-{noactive}' if noactive else ''}</td>
<td>{today-today_noactive if today-today_noactive else ''}{f'<br>-{today_noactive}' if today_noactive else ''}</td>
<td>{lastday-lastday_noactive if lastday-lastday_noactive else ''}{f'<br>-{lastday_noactive}' if lastday_noactive else ''}</td>
<td>{day_before_yesterday-day_before_yesterday_noactive if day_before_yesterday-day_before_yesterday_noactive else ''}{f'<br>-{day_before_yesterday_noactive}' if day_before_yesterday_noactive else ''}</td>
</tr>''')

    def get_table(self):
        rows = '\n'.join(self.rows)
        return f'''
        <table>
        {self.header}
        {rows}
        </table>
        '''

    def get_style(self, style_path):
        try:
            return open(style_path, 'r', encoding='utf-8').read()
        except:
            return

    def get_html(self, style_path,  title='Рекламная статистика', ) -> str:
        return f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="https://obertivanie.com/bot_images/ads/table1.css">
    {self.get_style(style_path)}
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
</head>
<body>
    <h1>{title}</h1>
    {self.get_table()}
</body>
</html>
        '''

    def save_page(self, style_path='table1.css', path='stats.html', title='Рекламная статистика'):
        if not DEBUG:
            open(path, 'w', encoding='UTF-8').write(self.get_html(style_path, title))
            




