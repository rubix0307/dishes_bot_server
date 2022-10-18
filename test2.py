
import os
from db.functions import sql


all_photos = sql('SELECT * FROM photos')


for index, data in enumerate(all_photos):
    local_photo = data['local_photo']
  
    image_path = '/var/www/admin/www/obertivanie.com/bot_images/' + local_photo
    status = os.path.exists(image_path)

    if not status:
        print(data['url'])

    