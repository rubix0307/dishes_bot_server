

import requests

from config import MEDIA_URL
from db.functions import sql

all_photos = sql('SELECT * FROM photos')
count_phs = len(all_photos)

continue_num = 950

for index, data in enumerate(all_photos):
    url = data['local_photo']

    if index < continue_num:
        continue

    status = requests.get(MEDIA_URL + url).ok

    if status:
        print(f'✅ {index}/{count_phs} ' + MEDIA_URL + url)
    else:
        print(f'🛑 {index}/{count_phs} ' + MEDIA_URL + url)

        open('dowload_images.txt', 'a').write(f'''{data['url']} >>> {url}''' + '\n')