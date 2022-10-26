



from pathlib import Path

from instagrapi import Client

from config import MEDIA_PATH
from functions import get_mailing_data


def instagram_mail(caption, photos_path: list[Path]):
    user = 'ukrainian.goods'
    password = 'qazwsxedcrfvtgbyhn9033'

    cl = Client()
    try:
        sessionn_id = open(f'sessions/{user}.txt', 'r').read()
        cl.login_by_sessionid(sessionn_id)
    except:
        cl.login(user, password)
        open(f'sessions/{user}.txt', 'w').write(cl.sessionid)

    cl.album_upload(
        paths= photos_path,
        caption=caption
    )



article, nexts_mailing = get_mailing_data(castom_dish_id=1)
photos = [MEDIA_PATH + ph for ph in article.data['photos'].split('\n')][:10]


instagram_mail(article.title, photos)

print()
