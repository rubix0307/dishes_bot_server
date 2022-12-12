import datetime
import os
import random
from pathlib import Path

import requests
from aiogram import types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.exceptions import ChatNotFound, BotBlocked
from aiogram.utils.markdown import *
from instagrapi import Client

from app import bot
from config import (ADMIN_ID, DEBUG, GROUG_ID, GROUP_LINK, MEDIA_PATH, MEDIA_URL,
                    NAKRUKA_KEY, instagram_pass, instagram_user)
from db.functions import sql
from functions import get_mailing_data, update_last_message
from markups import get_home_button

br = '\n'

def instagram_client_auth() -> Client:
    cl = Client()
    try:
        sessionn_id = open(f'sessions/{instagram_user}.txt', 'r').read()
        cl.login_by_sessionid(sessionn_id)
    except:
        cl.login(instagram_user, instagram_pass)
        open(f'sessions/{instagram_user}.txt', 'w').write(cl.sessionid)
    
    return cl

def instagram_mail(caption, photos_path: list[Path]):
    try:
        global cl
        cl
    except:
        cl = instagram_client_auth()

    try:
        answer = cl.album_upload(
            paths=photos_path,
            caption=caption
        )
        return answer
    except Exception as e:
        print(e)
    


def nakrutka_api(
    quantity,
    link,
    key=NAKRUKA_KEY,
    action='create',
    service=1,
):
    return requests.get(f'https://nakrutka.com/api/?key={key}&action={action}&service={service}&quantity={quantity}&link={link}')


async def mailing_dishe(castom_dish_id: int = None):
    try:
        article, nexts_mailing = get_mailing_data(
            castom_dish_id=castom_dish_id)

        media = types.MediaGroup()
        photos = article.data['photos'].split('\n')[:9]
        if not DEBUG:
            [media.attach_photo(types.InputFile(MEDIA_PATH + photo), article.title) for photo in photos]
        else:
            phs = os.listdir('images')
            [media.attach_photo(types.InputFile('images/' + photo), article.title) for photo in phs]
            photos = ['images/' + photo for photo in phs]


        if not DEBUG:
            show_preview = False
            try:
                if len(photos) > 1:
                    await bot.send_media_group(
                        media=media,
                        protect_content=True,
                        chat_id=GROUG_ID,
                        disable_notification=True,
                    )
                else:
                    show_preview = True
            except TypeError:
                show_preview = True


            
            await bot.send_message(
                text=article.get_message_text(show_preview=show_preview),
                reply_markup=article.get_markup(),
                parse_mode='html',
                chat_id=GROUG_ID,
                disable_notification=True,
                disable_web_page_preview=True,
            )

        try:
            instagram_text = article.get_message_text(is_send_instagram=True)
            post_code = instagram_mail(instagram_text, photos).code
            link = f'https://www.instagram.com/p/{post_code}'
            await bot.send_message(chat_id=ADMIN_ID, text=f'Успешно отправлено в instagram{br}{link}')
        except Exception as ex:
            await bot.send_message(chat_id=ADMIN_ID, text=f'Не удалось отправить в instagram{br*2}{ex}')

        try:
            nakrutka_api(
                quantity=random.randint(10, 35),
                link=link,
                service=1
            )
        except Exception as ex:
            await bot.send_message(chat_id=ADMIN_ID, text=f'Не удалось накрутить{br*2}{ex}')

        if nexts_mailing > -1:
            await bot.send_message(chat_id=ADMIN_ID, text=f'Количество блюд в рассылке: {nexts_mailing}')

    except Exception as e:
        print(e)
        pass


async def subscribe_to_group(all=False):
    all_users = sql(f'''SELECT * FROM `users` WHERE user_id NOT IN (SELECT user_id FROM `mailing_user`);''')

            
    caption = f'''⠀{br}Чудесный шанс: подпишись на наш {hlink('канал', GROUP_LINK)} и получай каждый день ещё больше идей рецептов, ещё больше блюд! '''
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Присоединиться', url=GROUP_LINK))
    now = datetime.datetime.now()
    date = f'{now.year}-{now.month}-{now.day}'
    photo = open(f'{MEDIA_PATH}default/ph_group.jpg', 'rb').read() if not DEBUG else open(f'images/ph_group.jpg', 'rb').read()
    
    mails = 0
    errors = 0
    for data in (all_users if not DEBUG else [{'user_id' : ADMIN_ID}]):
        user_id = data['user_id']
        try:
            message_data = await bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=caption,
                reply_markup=markup,
                protect_content=True,
                disable_notification=True,
                parse_mode='html'
            )
            sql(f'''UPDATE `users` SET `is_active` = '1' WHERE `users`.`user_id` = {user_id};''')
            is_update = sql(f'''INSERT INTO `mailing_user`(user_id, date, message_id) VALUES ({user_id},'{date}', {message_data.message_id})''', commit=True)
            if not is_update:
                sql(f'''UPDATE mailing_user SET date = '{date}' WHERE user_id = {user_id}; ''', commit=True)
            
            mails += 1
        except:
            sql(f'''UPDATE users SET is_active = '0' WHERE user_id = {user_id};''', commit=True)
            errors += 1
            continue


    await bot.send_message(chat_id=ADMIN_ID, text=f'Рассылка о подписке на группу{br}Отправлено: {mails}{br}Не отправлено: {errors}')

        

