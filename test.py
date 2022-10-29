



import os
from pathlib import Path

from instagrapi import Client
import requests

from config import MEDIA_PATH
from functions import get_mailing_data


def instagram_mail(article):
    user = 'best_recipe_insta'
    password = 'qazwsxedcrfvtgbyhn9033'

    cl = Client()
    try:
        sessionn_id = open(f'sessions/{user}.txt', 'r').read()
        cl.login_by_sessionid(sessionn_id)
    except:
        cl.login(user, password)
        open(f'sessions/{user}.txt', 'w').write(cl.sessionid)


    # photos = [MEDIA_PATH + ph for ph in article.data['photos'].split('\n')][:10]
    photos = ['images/' + ph for ph in os.listdir('images')]

    media_path = cl.photo_download(2957747669120614609, folder='mailing_imgs')

    photos.append(media_path)
    cl.album_upload(
        paths= photos,
        caption=article.get_message_text(show_preview=False)
    )



# article, nexts_mailing = get_mailing_data(castom_dish_id=1)

# instagram_mail(article)

# print()


import requests


answer = requests.get('https://nakrutka.com/api/?key=ca5a2c41f083f39ea151f195f70ce034&action=create&service=1&quantity=10&link=https://www.instagram.com/p/CkNp2Bis4Ju/')

print(answer)