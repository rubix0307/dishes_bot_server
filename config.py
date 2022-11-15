import os
import dotenv


dotenv.load_dotenv('.env')
BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_URL = 'https://t.me/best_recipe_bot'

MEDIA_URL = 'https://obertivanie.com/bot_images/'
MEDIA_PATH = '/var/www/admin/www/obertivanie.com/bot_images/'

GROUG_ID = int(os.environ['GROUG_ID'])
GROUP_LINK = 'https://t.me/best_recipe_group'
ADMIN_ID = 887832606
BUY_AD_URL = 'https://t.me/xx_rubix_xx'

NAKRUKA_KEY = os.environ['nakruka_key']

db_user = os.environ['db_user']
db_password = os.environ['db_password']

instagram_user = os.environ['instagram_user']
instagram_pass = os.environ['instagram_pass']

DEBUG = os.path.exists('DEBUG')
if DEBUG:
    print(f'🛑 {DEBUG=}')






