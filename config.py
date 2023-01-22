import os
import dotenv

dotenv.load_dotenv('.env')

BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_URL = 'https://t.me/best_recipe_bot'

MEDIA_URL = 'https://obertivanie.com/bot_images/'
MEDIA_PATH = '/var/www/admin/www/obertivanie.com/bot_images/'

GROUP_ID = int(os.environ['GROUP_ID'])
GROUP_LINK = 'https://t.me/best_recipe_group'
ADMIN_ID = 887832606

DB_USER = os.environ['db_user']
DB_PASSWORD = os.environ['db_password']

BUY_AD_URL = 'https://t.me/xx_rubix_xx'

LINK_SEPARATOR = '__'

DEBUG = os.path.exists('DEBUG')
if DEBUG:
    print(f'🛑 Debug mode')
