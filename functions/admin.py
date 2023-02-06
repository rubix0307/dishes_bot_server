
import asyncio
import datetime
import re
import threading

import aioschedule
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.exceptions import MessageCantBeForwarded, ChatNotFound, CantInitiateConversation
from aiogram.utils.markdown import hlink
from telethon.sync import TelegramClient

from app import bot
from config import ADMIN_ID, DEBUG, GROUP_ID, TELETHON_API_HASH, TELETHON_API_ID, TELETHON_PHONE, telethon_client

from .db import sql
from .main import check_start_photo, get_current_date, get_user_role, update_last_message
from .markups import (get_home_button, mails_call_filter, mails_call_menu,
                      set_channel_call_menu)


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
<td>{count-noactive}{f'<div class="min">-{noactive}</div>' if noactive else ''}</td>
<td>{today-today_noactive if today-today_noactive else ''}{f'<div class="min">-{today_noactive}</div>' if today_noactive else ''}</td>
<td>{lastday-lastday_noactive if lastday-lastday_noactive else ''}{f'<div class="min">-{lastday_noactive}</div>' if lastday_noactive else ''}</td>
<td>{day_before_yesterday-day_before_yesterday_noactive if day_before_yesterday-day_before_yesterday_noactive else ''}{f'<div class="min">-{day_before_yesterday_noactive}</div>' if day_before_yesterday_noactive else ''}</td>
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
            return ''

    def get_html(self, style_path,  title='Рекламная статистика', ) -> str:
        return f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{self.get_style(style_path)}</style>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand()
    </script>


</head>
<body>
    <h1>{title}</h1>
    {self.get_table()}
</body>
</html>
        '''

    def save_page(self, style_path='table1.css', path='stats.html', title='Рекламная статистика'):
        open(path, 'w', encoding='UTF-8').write(self.get_html(style_path, title))
            

def format_string(day, noactive):
    if day:
        return f"{day-noactive if day  else 'ㅤ'} {f'(-{noactive})' if noactive else ''}"
    else:
        return 'ㅤ'



async def notification_mailing():
    try:
        await bot.send_message(
            chat_id=437851430,
            text='Нужно сделать рассылку'
        )
    except:
        pass

def get_not_sended_top_post_data(user_id, channels, top_posts, channels_dict):
    user_sended_posts = sql(f'''SELECT * FROM `mailing_user` WHERE user_id = {user_id}''')
    channels_posts_user = {channel['id']: [] for channel in channels}
    
    for post in user_sended_posts:
        if post.get('channel_id', False):
            channels_posts_user[post['channel_id']].append(post['channel_msg_id'])

    for top_post in top_posts:
        if not top_post['post_id'] in channels_posts_user[top_post['channel_id']]:
            channel_id = top_post['channel_id']
            message_id = top_post['post_id']
            from_chat_id = channels_dict[channel_id]['channel_id']
            return channel_id, message_id, from_chat_id
    return None, None, None

async def send_message_all_admins(text):
    all_admins = sql(f'''SELECT user_id FROM `users` WHERE role_id = 2''')

    for admin in all_admins:
        await bot.send_message(chat_id=admin['user_id'], text=text)

async def send_top_posts(only_new_users_by_hour=True):
    if only_new_users_by_hour:

        users = sql(f'''
            SELECT DISTINCT u.user_id
            FROM users as u 
            WHERE u.is_active AND NOT u.is_send_after_hour_subs AND u.date <= NOW() - INTERVAL 1 HOUR;
        ''')

    else:
        users = sql(f'''
            SELECT DISTINCT u.user_id
            FROM users as u
            WHERE NOT u.date >= DATE(CURDATE())
        ''')



    top_posts = sql(f'''SELECT channel_id, post_id FROM `channels_posts` WHERE text != '' AND text NOT LIKE "%#НовыйГод%" ORDER BY `forwards` DESC LIMIT 20''')
    
    channels = sql(f'''SELECT * FROM `channels`''')
    channels_dict = {channel['id']: channel for channel in channels}
        
    channel_id = None
    message_id = None
    sends = 0
    sended_all_top_posts = 0
    errors = 0

    for user in users:
        user_id = user['user_id']

        channel_id, message_id, from_chat_id = get_not_sended_top_post_data(user_id, channels, top_posts, channels_dict)

        if channel_id and message_id and from_chat_id:
            try:

                answer = await bot.forward_message(
                    chat_id=user_id,
                    from_chat_id=from_chat_id,
                    message_id=message_id,
                )
                sql(f'''INSERT INTO `mailing_user`(`user_id`, `channel_id`, `channel_msg_id`, `date`, `message_id`) VALUES ("{user_id}", "{channel_id}", "{message_id}", "{get_current_date()}", {answer.message_id})''', commit=True)
                sql(f'''UPDATE `users` SET `is_send_after_hour_subs` = '1', `is_active` = '1' WHERE `users`.`user_id` = {user_id};''', commit=True)
                
                sends += 1
                print(f'Авторассылка{br}Отправлено: {sends}{br}Не отправлено: {errors}')
            except Exception as ex:
                sql(f'''UPDATE `users` SET `is_active` = '0' WHERE `users`.`user_id` = {user_id};''', commit=True)
                errors += 1
        else:
            sended_all_top_posts += 1
    if users:
        try:
            last_mails = sql(f'''SELECT * FROM `mailing_after_hour_subs` WHERE `date` = "{get_current_date()}"''')
            sql(f'''UPDATE `mailing_after_hour_subs` SET `sends`={last_mails[0]['sends'] + sends},`errors`={last_mails[0]['errors'] + errors} WHERE `date` = "{get_current_date()}"''', commit=True)
        except:
            sql(f'''INSERT INTO `mailing_after_hour_subs`(`sends`, `errors`) VALUES ({sends},{errors})''', commit=True)

        if not only_new_users_by_hour:
            await send_message_all_admins(f'Ежедневная авторассылка топ постов{br*2}Отправлено: {sends}/{len(users)}{br}Не отправлено: {errors}{br*2}Нет новых постов для: {sended_all_top_posts}')

async def get_stats_by_after_hour_subs(message: types.Message=None):
    

    if message:
        user_id = message.from_user.id
    else:
        user_id = ADMIN_ID


    last_mails = sql(f'''SELECT * FROM `mailing_after_hour_subs` WHERE `date` = "{get_current_date()}"''')[0]
    await bot.send_message(chat_id=user_id, text=f'''Ежедневный отчет по авто-рассылке{br}Отправлено: {last_mails['sends']}{br}Не отправлено: {last_mails['errors']}''')


async def channel_subscription_notification():
    all_active_users = sql(f'''SELECT u.user_id FROM users as u WHERE u.is_active ORDER BY u.role_id DESC''')
    
    sends = 0
    errors = 0

    for user in all_active_users:
        try:
            user_id = user['user_id']
            user_channel_status = await bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
            print(user_channel_status.status)

            if user_channel_status.status == 'left':
                is_send = await check_start_photo(user_id, is_mandatory_sending=True)
                if is_send:
                    sends += 1
                else:
                    sql(f'''UPDATE `users` SET `is_active` = '0' WHERE `users`.`user_id` = {user_id};''', commit=True)
                    errors += 1
            continue
        except:
            continue

    await bot.send_message(chat_id=ADMIN_ID, text=f'Напоминание о подписке на канал{br*2}Отправлено: {sends}{br}Не отправлено: {errors}')

async def scheduler():
    aioschedule.every(10).minutes.do(send_top_posts, only_new_users_by_hour=True)
    aioschedule.every().day.at("13:01").do(send_top_posts, only_new_users_by_hour=False)

    # aioschedule.every().day.at("13:00").do(notification_mailing)
    # aioschedule.every().day.at("19:00").do(notification_mailing)
    aioschedule.every().day.at("23:55").do(get_stats_by_after_hour_subs)

    aioschedule.every(5).days.at("10:00").do(channel_subscription_notification)


    while True:
        if DEBUG:
            print('[DEBUG] Проверка scheduler')
        await aioschedule.run_pending()
        await asyncio.sleep(60)








br = '\n'
line = '—'*22
mailing_cancel_data = 'Для отмены рассылки — /cancel'
default_text = 'Текст не указан ⭕️'
default_channel_name = 'не выбран ⭕️'
class Form(StatesGroup):
    text = State()
    photo = State()
    disable_web_page_preview = True
    share_state = False

def get_action(text, action_name):
    return InlineKeyboardButton(
        text=text,
        callback_data=mails_call_menu.new(action=mails_call_filter[action_name]))

async def set_default_data_mails(data):

    data['text'] = data.get('text', default_text)
    data['self_view'] = data.get('self_view', False)
    data['set_channel'] = data.get('set_channel', None)
    data['paddings_state'] = data.get('paddings_state', False)
    data['protect_content'] = data.get('protect_content', False)
    data['disable_web_page_preview'] = data.get('disable_web_page_preview', True)

    if not 'share_state' in data.keys() or data['text'].isdigit():
        data['share_state'] = data['text'].isdigit()


    data['channel_id'] = data.get('channel_id', GROUP_ID)
    data['channel_info'] = data.get('channel_info', await bot.get_chat(chat_id=data['channel_id']))



async def send_or_edit_message(message, message_data):
    try:
        try:
            answer = await message.message.edit_text(**message_data)
        except:
            answer = await message.message.answer(**message_data)
            await message.message.delete()
    except:
        answer = await message.answer(**message_data)
        await update_last_message(message, castom_message_id=answer.message_id)
        await message.delete()
    return answer

async def mailing_cancel(message: types.Message, state=FSMContext):
    message_data = {
        'text': 'Рассылка отменена',
        'reply_markup': InlineKeyboardMarkup().add(get_home_button('На главную'))
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
    share_state = f'''Взять с канала {'✅' if data['share_state'] else '❌'}'''
    protect_content_state = f'''Копирование: {'✅' if not data['protect_content'] else '❌'}'''

    edit_channel = f'Изменить канал'

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(get_action('Изменить текст', 'edit_text'))

    if 'http' in data['text']:
        markup.add(get_action(web_page_preview_state, 'preview_state'))

    
    if not data['share_state']:
        markup.add(get_action(paddings_state, 'paddings_state'))
    else:
        markup.add(get_action(edit_channel, 'edit_channel'))


    markup.add(get_action(protect_content_state, 'protect_content_state'))

    if data['text'].isdigit():
        markup.add(get_action(share_state, 'share_state'))


        
    markup.add(get_action('Отправить себе', 'self_send'))
    if data['self_view']:
        markup.add(get_action('Отправить всем', 'send_all'))


    channel_info = f'''{br}Канал: [{data['channel_info'].title}](https://t.me/{data['channel_info'].username}){br}''' if data['share_state'] else ''

    message_data = {
        'text' : f'''{mailing_cancel_data}{channel_info}{br*2}Текущий текст:{br}{line}{br}{data['text']}''',
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

async def edit_channel(message: types.CallbackQuery, state: FSMContext):


    reply_markup = InlineKeyboardMarkup()

    channels = sql(f'''SELECT * FROM `channels`''')

    for channel in channels:
        channel_data = await bot.get_chat(channel['channel_id'])

        reply_markup.add(
            InlineKeyboardButton(text=channel_data.title, callback_data=set_channel_call_menu.new(id=channel_data.id))
        )


    message_data = {
        'text': f'Выберите канал для выбора поста',
        'reply_markup': reply_markup,
    }

    await message.message.answer(**message_data)
    await message.message.delete()

async def set_channel(message: types.CallbackQuery, state: FSMContext, callback_data: dict()):
    
    channel_id = callback_data.get('id')
    async with state.proxy() as data:
        data['channel_id'] = channel_id
        data['channel_info'] = await bot.get_chat(chat_id=data['channel_id'])
        data['self_view'] = False
        await get_preview_mail(message, data)


    

  
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

async def send_stats_curr_mail(chat_id, mails, errors, has_this_post, message_data, num, max_users,edit=True, message_id=None, is_share = False, data_text=''):
    has_this_post_info = f'{br}Уже имеют: {has_this_post}{br}' if has_this_post else ''
    if not is_share:
        data = {
            'chat_id': chat_id,
            'text': f'''Рассылка {num+1}/{max_users}{br}Отправлено: {mails}{br}Не отправлено: {errors}{has_this_post_info}{br*2}Сообщение рассылки:{br}{line}{br}{message_data['text']}''',
            'disable_web_page_preview': message_data['disable_web_page_preview'],
            'parse_mode': message_data['parse_mode'],
        }
    else:
        data = {
            'chat_id': chat_id,
            'text': f'''Рассылка {num+1}/{max_users}{br}Отправлено: {mails}{br}Не отправлено: {errors}{has_this_post_info}{br*2}Пересылается сообщение {hlink(f'№{data_text}', f'https://t.me/best_recipe_group/{data_text}')} с группы''',
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

            db_data = {}

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
                    'from_chat_id': data['channel_id'],
                    'message_id' :  int(data['text']),
                    'protect_content' : data['protect_content'],
                }
                

                id_for_db = sql(f'''SELECT * FROM `channels` WHERE channel_id = "{data['channel_id']}"''')
                db_data = {
                    'channel_id_for_db': id_for_db[0]['id'],
                    'channel_msg_id': int(data['text']),
                }

        if only_me:
            try:
                answer = await mail_function(chat_id=chat_id, **message_data)
            except MessageCantBeForwarded:
                return await message.answer('нельзя переслать сообщение')
            await message.answer()
            await asyncio.sleep(3)
            await bot.delete_message(chat_id=chat_id, message_id=answer.message_id)
            async with state.proxy() as data:
                data['self_view'] = True
                await get_preview_mail(message, data)
            

        elif role in [2,3] and not only_me:
            all_users = sql(f'''SELECT * FROM `users` ORDER BY `users`.`role_id` DESC''')
            max_users = len(all_users)
            now = datetime.datetime.now()
            date = f'{now.year}-{now.month}-{now.day}'
            
            mails = 0
            errors = 0
            has_this_post = 0

            

            stats_message = await send_stats_curr_mail(chat_id, mails, errors, has_this_post, message_data, 0, max_users, edit=False, is_share=share_state, data_text=data_text)


            try:
                await message.message.delete()
            except:
                pass
            await state.finish()

            id_channel_in_db = db_data.get('channel_id_for_db', False)
            msg_id = db_data.get('channel_msg_id', False)

            for num, data in enumerate(all_users):

                if not num % 10:
                    await send_stats_curr_mail(chat_id, mails, errors,has_this_post, message_data, num, max_users, message_id=stats_message.message_id, is_share=share_state, data_text=data_text)


                user_id = data['user_id']

                
                if id_channel_in_db and msg_id:
                    data_count = sql(f'''
                        SELECT COUNT(*) as `count` FROM `mailing_user` 
                        WHERE `channel_id` = '{id_channel_in_db}' AND `channel_msg_id` = '{msg_id}' AND `user_id` = '{user_id}'
                        GROUP BY channel_msg_id
                    ''')
                    if len(data_count):
                        user_has_this_post = bool(data_count[0].get('count', 0))

                        if user_has_this_post:
                            has_this_post += 1
                            continue


                try:
                    answer = await mail_function(chat_id=user_id, **message_data)
                    sql(f'''UPDATE `users` SET `is_active` = '1' WHERE `users`.`user_id` = {user_id};''', commit=True)
                    is_insert = sql(f'''INSERT INTO `mailing_user`(`user_id`, `channel_id`, `channel_msg_id`, `date`, `message_id`) VALUES ({user_id},{db_data.get('channel_id_for_db', 'Null')},{db_data.get('channel_msg_id', 'Null')},"{date}", "{answer.message_id}")'''
, commit=True)
                    mails += 1
                except:
                    sql(f'''UPDATE users SET is_active = '0' WHERE user_id = {user_id};''', commit=True)
                    errors += 1
                    continue


            await send_stats_curr_mail(chat_id, mails, errors,has_this_post,  message_data, num, max_users, message_id=stats_message.message_id, is_share=share_state, data_text=data_text)

    except Exception as ex:

        pass



async def get_client(api_id: int = TELETHON_API_ID,api_hash: str = TELETHON_API_HASH, file_name: str = 'sessions/checker_account3',proxy=(2, '149.154.167.91', 443),) -> TelegramClient:
    proxy = None
    client = TelegramClient(file_name, api_id, api_hash, proxy=proxy)
    client.castom_data = {
        'file_name': file_name,
        'proxy': proxy,
    }
    try:
        await client.start(phone=TELETHON_PHONE)
        return client
    except:
        print(f'FAIL {file_name}')
        return False



async def update_stats_by_channels_posts():
    global client

    try:
        if not client:
            client = await get_client(proxy=None, )
            print('Создаю клиент')
        else:
            print('Клиент есть')
    except:
        client = await get_client(proxy=None, )
        print('Ошибка, cоздаю клиент')
    
    if not client:
        await bot.send_message(chat_id=ADMIN_ID, text='Telethon client is not available')
        return
    last_grouped_id = None
    channels = sql(f'''SELECT id, channel_id FROM `channels`''')
    posts = 2000


    for channel in channels:
        channel_id, dialog_id = channel.values()
        all_posts = [post_id['post_id'] for post_id in sql(f'''SELECT post_id FROM `channels_posts` WHERE channel_id = {channel_id}''')]


        messages = await client.get_messages(dialog_id, limit=posts)
        for message in messages:
            
            try:
                print(f'https://t.me/{message._sender.username}/{message.id}')
            except:
                pass

            if last_grouped_id == message.grouped_id and message.grouped_id:
                continue
            last_grouped_id = message.grouped_id


            date = message.date
            date_formated = f'{date.year}-{date.month}-{date.day} {date.hour}:{date.minute}:00'
            
            if not message.id in all_posts:
                sql(f'''
                INSERT INTO `channels_posts`
                (`channel_id`, `post_id`, `views`, `forwards`, `photo_id`, `button_count`, `text`, `is_forward`, `is_noforwards`, `is_reply`, `is_pinned`, `date`)
                VALUES 
                ('{channel_id}',{message.id},{message.views if message.views else 'Null'},{message.forwards if message.forwards else 'Null'},{message.photo.id if message.photo else 'Null'},{message.button_count},'{message.text}','{int(bool(message.forward))}','{int(bool(message.noforwards))}','{int(bool(message.is_reply))}','{int(bool(message.pinned))}','{date_formated}')
                ''', commit=True)
            else:
                update_data = [
                    ['views', message.views if message.views else 0],
                    ['forwards', message.forwards if message.forwards else 0],
                    ['photo_id', message.photo.id if message.photo else 0],
                    ['is_pinned', int(bool(message.pinned))],
                    ['text', message.text.replace('"', '\\"').replace("'", "\\'") if message.text else ' '],
                ]

                
                set_query = ', '.join([f'`{value[0]}`= "{value[1]}"' for value in update_data])
                sql(f'''UPDATE `channels_posts` SET {set_query} WHERE `channel_id` = "{channel_id}" AND `post_id` = "{message.id}"''', commit=True)









