import os
import dotenv


dotenv.load_dotenv('.env')
BOT_TOKEN = os.environ['BOT_TOKEN']
db_user = os.environ['db_user']
db_password = os.environ['db_password']

GROUG_ID = int(os.environ['GROUG_ID'])
ADMIN_ID = 887832606
BUY_AD_URL = 'https://t.me/xx_rubix_xx'

MEDIA_URL = 'https://obertivanie.com/bot_images/'
MEDIA_PATH = '/var/www/admin/www/obertivanie.com/bot_images/'
BOT_URL = 'https://t.me/best_recipe_bot'

