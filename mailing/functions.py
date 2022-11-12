import os
from pathlib import Path
import random

import requests
from aiogram import types
from aiogram.utils.exceptions import ChatNotFound
from app import bot
from config import ADMIN_ID, GROUG_ID, MEDIA_PATH, MEDIA_URL, NAKRUKA_KEY
from instagrapi import Client

from functions import get_mailing_data
from config import instagram_user, instagram_pass, DEBUG

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
                        disable_notification=DEBUG,
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
                disable_notification=DEBUG,
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
