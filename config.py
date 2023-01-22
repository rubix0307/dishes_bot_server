import os
import dotenv

dotenv.load_dotenv('.env')

BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_URL = 'https://t.me/best_recipe_bot' # Check out the bot at this link

MEDIA_URL = os.environ['MEDIA_URL']
MEDIA_PATH = os.environ['MEDIA_PATH']

GROUP_ID = int(os.environ['GROUP_ID'])
GROUP_LINK = os.environ['GROUP_LINK']
ADMIN_ID = int(os.environ['ADMIN_ID'])

DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']

BUY_AD_URL = os.environ['BUY_AD_URL']

LINK_SEPARATOR = '__'

DEBUG = os.path.exists('DEBUG')
if DEBUG:
    print(f'🛑 Debug mode')
