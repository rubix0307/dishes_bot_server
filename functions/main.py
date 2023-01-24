
import asyncio
import copy
import time
from datetime import datetime

import pymorphy2
from aiogram import Bot, types
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.markdown import *

from config import ADMIN_ID, BOT_URL, BUY_AD_URL, DEBUG, LINK_SEPARATOR, MEDIA_URL
from . import db
from .markups import *
from app import bot

br = '\n'

def log(msg, error=True):
    
    prefix = '🛑' if error else ''
    answer = f'{prefix} {datetime.now()} | {msg}{br}'
    print(answer)
    open('log.txt', 'a' , encoding='utf-8').write(answer)


morph = pymorphy2.MorphAnalyzer()
def get_normal_form(text: str):
    global morph
    if text:
        text = text.replace('(', '').replace(')', '').replace('\'', '')

        prelogs = [' без ', ' безо ', ' близ ', ' в ',  ' во ', ' вместо ', ' вне ', ' для ', ' до ', ' за ', ' из ', ' изо ', ' и ', ' к ',  ' ко ', ' кроме ', ' между ', ' меж ', ' на ', ' над ', ' надо ', ' о ',  ' об ', ' обо ', ' от ', ' ото ', ' перед ', ' передо ', ' предо ', ' пo ', ' под ', ' при ', ' про ', ' ради ', ' с ',  ' со ', ' сквозь ', ' среди ', ' через ', ' чрез ']
        for sumb in prelogs:
            text = text.replace(sumb, ' ')

        normal_form = [morph.parse(i)[0].normal_form for i in text.split()]

        return ' '.join(normal_form)
    else:
        return text

def get_user_role(user_id) -> int:
        user_role = db.sql(f'SELECT `role_id` FROM `users` WHERE `user_id` = {user_id}')
        if user_role:
            return user_role[0]['role_id']
        else:
            return 1

def get_home_page(user_id:int=1, btn_title=None, btn_search=None, add_title_row=None) -> dict:
    text = 'Добро пожаловать в бот'
    if add_title_row:
        text = f'{text}{br}{add_title_row}'
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=f'♥️ Избранное', switch_inline_query_current_chat=filters['favorites']))
    markup.add(InlineKeyboardButton(text=f'🌍 Кухни мира 🌎', callback_data=show_menu.new(menu_name=call_filters['countries'])))
    markup.add(InlineKeyboardButton(text=f'🗂 По категориям', callback_data=show_menu.new(menu_name=call_filters['categories'])))
    markup.add(InlineKeyboardButton(text=f'🧾 Искать рецепт' if not btn_title else btn_title, switch_inline_query_current_chat='' if not btn_search else btn_search))
    markup.add(InlineKeyboardButton(text=f'👩‍👦‍👦 Наши группы 🆕', callback_data=show_menu.new(menu_name=call_filters['groups'])))
    markup.add(InlineKeyboardButton(text=f'🎄 КОНКУРС НА 50$ 🌟', callback_data=show_menu.new(menu_name=call_filters['contest'])))

    if btn_title or btn_search:
        markup._values['inline_keyboard'].insert(0, markup._values['inline_keyboard'][3])
        markup._values['inline_keyboard'].pop(4)
    

    if get_user_role(user_id) == 2:
        markup.add(
            # InlineKeyboardButton(text=f'🤖 Рассылка', switch_inline_query_current_chat=filters['mailing']),
            InlineKeyboardButton(text=f'🤖 Реклама', callback_data=get_ads_stats_call_menu.new()),
        )



    return {
        'text': text,
        'reply_markup': markup,
        'parse_mode': 'html',
    }


def user_activity_record(user_id: int, dish_id: int, query_text: str):
    sql_query = f'''
    INSERT INTO users_actions (user_id, dish_id, query_text) 
    VALUES 
    ({user_id},{dish_id},"{query_text}")
    '''
    db.sql(sql_query, commit=True)



def buttons_list_categories(categories, highlight_symbol):
    keyboard_markup = InlineKeyboardMarkup()
    for category in categories[:99]:

        title = category['title'].replace(highlight_symbol, '').strip().split(' ')[0][:12].lower()

        keyboard_data = {
            'text': category['title'],
            'switch_inline_query_current_chat': f'''{filters['category']}{title}''',
        }

        keyboard_markup.add(InlineKeyboardButton(**keyboard_data,))
    return keyboard_markup

async def contest(message: types.Message, is_callback=False):
        user_id = message.from_user.id
        role_id = get_user_role(user_id)
        

        contest_users = db.sql(f'''
SELECT u2.user_id as id, u2.first_name as name, COUNT(*) as count 
FROM users as u 
INNER JOIN users as u2 ON u.came_from = u2.user_id 
WHERE NOT (u.came_from REGEXP '[^0-9]') AND u.date <= '2022-12-30'
GROUP BY u.came_from  
ORDER BY `count`  DESC''')

        you = {
            'pos': 0,
            'count': 0,
        }
        for num, data in enumerate(contest_users):
            if data['id'] == user_id:
                you.update({
                    'pos': num +1,
                    'count': data['count'],
                })

        fake = [
            {'id': 4762550621, 'name': 'Alexander', 'count': 2},
            {'id': 4762550622, 'name': 'Марина', 'count': 2},
            {'id': 4762550623, 'name': 'Ксения', 'count': 2},
            {'id': 4762550624, 'name': 'Ирина', 'count': 1},
            {'id': 4762550625, 'name': 'Oksi', 'count': 1},
        ]
        for i in fake:
            if role_id == 2:
                i['name'] = '🔻' + i['name']

            contest_users.append(i)
        

        msg = f'''{hbold('СКОРО НОВЫЙ КОНКУРС')}
А ПОКА, КОНКУРС ЗАВЕРШЕН - {hlink('РЕЗУЛЬТАТЫ','https://t.me/best_recipe_group/622')}

Пригласите как можно больше людей в наш бот по своей реферальной ссылке и станьте победителем 💵🍾
Конкурс проходит до Нового Года🎄

⛔️Обратите внимание, что участники, которые уже участвуют в конкурсе, или подписались по другой ссылке, не могут принять участие по вашей ссылке. Также не будут засчитываться участники, которые подписались и сразу отписались. В зачет пойдут только пользователи, подписанные на наш кулинарный бот к моменту завершения конкурса.

Призовой фонд разделится следующим образом:
1️⃣ место - 25 долларов
2️⃣ место - 15 долларов
3️⃣ место - 10 долларов

Результаты будут объявлены 31.12.2022
Способ выплаты призовых будет согласован с победителями в индивидуальном порядке для их удобства.
Удачи!

{f"📶 Ты пригласил {you['count']} человек.{br}Статистика конкурса открывается только для участников в этом же меню" if not you['pos'] else f"📶 Ты занимаешь {you['pos']} место{br}пригласил {you['count']} человек"},
    
📌 Твоя реферальная ссылка:
{BOT_URL}?start={user_id}

Быстрое приглашение друзьям:
(нажми на него что б скопировать)
{hcode(f'Мне нравится этот телеграмм бот с рецептами.{br}Советую тебе подписаться на них по моей ссылке,{br}ведь они сейчас проводят конкурс!💵{br}{BOT_URL}?start={user_id}')}


📶 ТОП 10 пригласивших:
{f'(таблица видна только участникам конкурса, т.е. успешно пригласившим хотя бы одного пользователя)' if not you['count'] else ''}


'''

        markup = InlineKeyboardMarkup(row_width=3)
        
        
        if contest_users:
            markup.add(*[get_nothing_button(f'№'), get_nothing_button(f'участник'), get_nothing_button(f'''пригласил''')])

        for num, data in enumerate(contest_users[:10]):
            # if you['pos'] <= num + 2 and you['pos'] >= num and you['pos']:
            #     count = data['count']
            # else:
            #     count = f'''- {data['count']} -''' if role_id == 2 else '❓'


            # finished contest
            count = data['count']

            markup.add(*[get_nothing_button(f'''{f'- {num + 1} - ' if data['id'] == user_id else num + 1 }'''), get_nothing_button(data['name'][:20]), get_nothing_button(count)])
            


        markup.add(get_home_button('🎄 На главную 🌟'))


        if not is_callback:
            answer = await message.answer(msg, reply_markup=markup, disable_web_page_preview=True, parse_mode='html')
            user_activity_record(user_id, 0, message.text)
            await message.delete()
        else:
            answer = await bot.send_message(chat_id = user_id, text=msg, reply_markup=markup, disable_web_page_preview=True, parse_mode='html')
            user_activity_record(user_id, 0, call_filters['contest'])
        await update_last_message(message, castom_message_id = answer.message_id)
    
async def send_categories(bot, call, message_data):
    try:
        await call.message.edit_text(**message_data,)
    except:
        try:
            await bot.edit_message_text(
                inline_message_id=call.inline_message_id,
                **message_data,
            )
        except:
            try:
                await bot.edit_message_text(
                    chat_id=call.from_user.id,
                    message_id=call.message_id,
                    **message_data,
                )
            except:
                answer = await bot.send_message(
                    chat_id=call.from_user.id,
                    **message_data,
                )
                await update_last_message(call, castom_message_id=answer.message_id)
                await call.delete()
                return
    await call.answer()

async def by_countries(bot, call, highlight_symbol = '⭐️ '):

    text = 'Кухни разных стран'
    top_categories = db.sql(
        f'SELECT title, emoji FROM `categories` WHERE favorite = 1')
    categories = db.sql(
        'SELECT title, emoji FROM categories WHERE parent_id = 1 AND is_show = 1')


    new_category_list = []
    
    max_len = max([len(category['title'].split()[0]) if not category['title'].split()[0] in ['Средиземноморская','Азербайджанская'] else 0  for category in categories])
    for category in categories:
        title = category['title'].split()[0]

        spase = '⠀'* (max_len - len(title))
        category['title'] = f'''{title} {spase}{category['emoji']}'''
        new_category_list.append(category)

    for category in top_categories:
        title = category['title'].split()[0]

        spase = '⠀'* (max_len - len(title))
        category['title'] = f'''{highlight_symbol} {title} {spase[:-1]}{category["emoji"]}'''
        new_category_list.append(category)

    categories = new_category_list

    answer = {
        'parse_mode': 'html',
        'reply_markup': buttons_list_categories(categories, highlight_symbol).add(get_home_button()),
        'text': text,  
    }
    await send_categories(bot, call, answer)
    
async def by_categories(bot, call, highlight_symbol = '⭐️ '):
    text = 'По категориям'
    categories = db.sql('SELECT title,emoji FROM categories WHERE parent_id = 2 AND is_show = 1')
    answer = {
        'parse_mode': 'html',
        'reply_markup': buttons_list_categories(categories, highlight_symbol).add(get_home_button()),
        'text': text,  
    }
    await send_categories(bot, call, answer)

async def get_home(call):
    message_data = get_home_page(call.from_user.id)

    try:
        await call.message.edit_text(**message_data)
    
    except Exception as ex:
        try:
            await bot.edit_message_text(
                inline_message_id=call.inline_message_id,
                **message_data,
            )
        except:
            answer = await bot.send_message(chat_id=call.from_user.id, **message_data,)
            await update_last_message(call, castom_message_id=answer.message_id)

    finally:
        await call.answer()
        return

async def groups(message: types.Message, is_callback=False):
    user_id = message.from_user.id

    markup = InlineKeyboardMarkup(row_width=3)
    
    markup.add(InlineKeyboardButton('📖 Книга Рецептов 🔥', url='https://t.me/+aIOTdrZd3504NGUy'))
    markup.add(InlineKeyboardButton('📖 Кулинарные Лайфхаки💡', url='https://t.me/+JKomHC4hlhQ2NTNi'))
    markup.add(get_home_button('🎄 На главную 🌟'))


    if not is_callback:
        answer = await message.answer_photo(photo='https://obertivanie.com/bot_images/default/sub_to_group.png', protect_content=True,
                reply_markup=markup, parse_mode='html')
        user_activity_record(user_id, 0, message.text)
        await message.delete()
    else:
        answer = await bot.send_photo(photo='https://obertivanie.com/bot_images/default/sub_to_group.png', protect_content=True, chat_id = user_id, reply_markup=markup, parse_mode='html')
        user_activity_record(user_id, 0, call_filters['groups'])
    await update_last_message(message, castom_message_id = answer.message_id)

async def update_last_message(message: types.Message, castom_user=None, castom_message_id = None):
    if not castom_user:
        try:
            user = message['from_user']
        except KeyError:
            user = message.from_user
        
    else:
        user = castom_user

    if not castom_message_id:
        message_id = message.message_id
    else:
        message_id = castom_message_id

    last_message = db.sql(f'SELECT message_id FROM users_messages WHERE user_id = {user["id"]}')
    
    if not len(last_message):
        db.sql(f'INSERT INTO `users_messages`(`user_id`, `message_id`) VALUES ({user["id"]},{message_id})', commit=True)
        last_message = [{'message_id': message_id}]

    elif not message_id == last_message[0]['message_id']:
        try:
            try:
                await bot.delete_message(
                        chat_id=user["id"],
                        message_id=last_message[0]['message_id']
                    )
            except:
                pass
        finally:
            db.sql(f'UPDATE users_messages SET message_id={message_id} WHERE user_id = {user["id"]}', commit=True)


class Dishes:

    def __init__(self,
        user_id: int,
        query: str = '',
        dishe_id: int = None,
        category: int or str = None,
        start:int = 0, stop:int = 50,
        parse_mode='html',
        callback_data=None,
        disable_notification=False,
        disable_web_page_preview=True,
        get_by_query=False,
        get_by_id=False,
        get_by_category=False,
        get_by_favorites=False,
    ):
        self.start_time = time.time()
        self.query = query[:24]
        self.normal_query = get_normal_form(query)
        self.user_id = user_id
        self.dishe_id = dishe_id
        
        self.start = start
        self.stop = stop

        self.start_time = time.time()

        self.parse_mode = parse_mode
        self.callback_data = callback_data if callback_data else self.get_default_callback_data()
        self.disable_notification = disable_notification
        self.disable_web_page_preview = disable_web_page_preview


        if get_by_query:
            self.get_by_query()

        elif get_by_id:
            self.get_by_id()

        elif get_by_category:
            inline_filter, category = self.query.split('=')
            self.get_by_category(category)
        
        elif get_by_favorites:
            self.get_by_favorites()

    def print_all_time(self, title: str = 'Затраченое время'):
        print(f'| {title} | {round(time.time() - self.start_time, 3)}')

    def get_default_callback_data(self):
        return {
            'id' : self.dishe_id,
            'fav' : int(self.dishe_id in self.get_favourites_user()),
            'query' : self.query if self.query else '',
            'num_ph' : 0,
        }

    def get_favourites_user(self):
        fav = db.get_fav_dish_by_user(self.user_id)
        fav = fav if fav else []
        fav_ids = [item['id'] for item in fav]
        return fav_ids

    def get_by_favorites(self):
        sql_query = f'''
        SELECT d.id, d.title, d.serving, d.cooking_time, d.kilocalories, 
            (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
            (select p.local_photo from photos as p where p.dish_id=d.id limit 1) as photos
        FROM dishes as d 
        WHERE d.id in (select dish_id from fav_dish_user where user_id = {self.user_id})
        ORDER BY d.likes DESC
        LIMIT {self.start},{self.stop}
        '''
        self.dishes_data_list = db.sql(sql_query)
        return self.dishes_data_list
    
    def get_by_category(self, category):
        if not category.isdigit():
            try:
                category = db.sql(f'SELECT SQL_CACHE id FROM categories WHERE title LIKE "{category}%" LIMIT 1')[0]['id']
            except:
                category = 27


        sql_query = f'''
            SELECT SQL_CACHE  d.*,
                (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                (select GROUP_CONCAT(p.local_photo SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos,
                (select GROUP_CONCAT(DISTINCT CONCAT(i.title,": ", di.value) SEPARATOR '\n') from ingredients as i INNER JOIN dishes_ingredients as di ON di.ingredient_id = i.id where di.dish_id=d.id) as ingredients
            FROM dishes as d

            LEFT JOIN dishes_categories as dc ON dc.dish_id = d.id
            LEFT JOIN categories as c ON c.id = dc.category_id
        
            WHERE dc.category_id = {category} 
            
            ORDER BY d.likes
            LIMIT {self.start},{self.stop}
        '''

        self.dishes_data_list = db.sql(sql_query)

        return self.dishes_data_list
    
    def get_by_query(self):
        self.dishes_data_list = db.sql(
            f'''SELECT  SQL_CACHE d.id, d.title, d.serving, d.cooking_time, d.kilocalories, 
                (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                (select GROUP_CONCAT(p.local_photo SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos
            FROM dishes as d 

            WHERE MATCH (d.norm_title, d.title) AGAINST ("{self.normal_query}")
            LIMIT {self.start}, {self.stop}'''
        )
        if not self.dishes_data_list:
            self.dishes_data_list = db.sql(
                f'''
                SELECT SQL_CACHE  d.id, d.title, d.serving, d.cooking_time, d.kilocalories,
                    (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                    (select GROUP_CONCAT(p.local_photo SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos
                FROM dishes as d 
                WHERE norm_title LIKE "%{self.normal_query}%"
                LIMIT {self.start},{self.stop}
            ''')

        return self.dishes_data_list

    def get_by_id(self):
        if self.dishe_id > 0:
            sql_query = f'''
            SELECT SQL_CACHE  d.id, d.title, d.original_link, d.serving, d.cooking_time, d.kilocalories,d.protein, d.fats, d.carbohydrates, d.recipe, d.likes,
                (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                (select GROUP_CONCAT(p.local_photo SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos,
                (select GROUP_CONCAT(DISTINCT CONCAT(i.title,": ", di.value) SEPARATOR '\n') from ingredients as i 
                INNER JOIN dishes_ingredients as di ON di.ingredient_id = i.id where di.dish_id=d.id
                ) as ingredients
            
            FROM dishes as d

            WHERE d.id = {self.dishe_id}
            '''
            self.dishes_data_list = db.sql(sql_query)
            return self.dishes_data_list

    def get_inline_description(self, dishes_data_list_item):
        if dishes_data_list_item['id'] > 0:
            if not dishes_data_list_item['categories']:
                dishes_data_list_item['categories'] = "-"*20

            description = f'''Порций: {dishes_data_list_item['serving']} | {dishes_data_list_item['cooking_time']} | {dishes_data_list_item['kilocalories']} ккал{br}{dishes_data_list_item['categories'].capitalize()}'''
        else:
            description = f'😢'
        return description

    def get_inline_thumb_url(self, dishes_data_list_item):
        thumb_url = dishes_data_list_item['photos'].split('\n')[0] if type(dishes_data_list_item['photos']) == str else (dishes_data_list_item['photos'][0] if dishes_data_list_item['photos'] else None)
        if not thumb_url:
            thumb_url = 'default/404.png'

        return MEDIA_URL + thumb_url

    def get_inline_input_message_content(self, dishes_data_list_item):
        return types.InputTextMessageContent(
            message_text= f"get_id={dishes_data_list_item['id']}{LINK_SEPARATOR}query_text={self.query}",
            parse_mode='html',
        )

    def get_inline_result(self):
        inline_result = []
        for data in self.dishes_data_list:
            try:
                inline_result.append(
                    types.InlineQueryResultArticle(
                        id=data['id'],
                        title=data['title'],
                        thumb_url=self.get_inline_thumb_url(data),
                        description=self.get_inline_description(data),
                        input_message_content=self.get_inline_input_message_content(data),
                    )
                )
            except Exception as ex:
                log(f'''get_inline_result | {ex} | query = {self.query} | user_id = {self.user_id} | dishe_id = {data['id']}''')
        
        return inline_result

    def get_blank_inline_result(self, id=0, title='К сожалению ничего не найдено.', photo='default/404.png', ):
        self.dishes_data_list = [{
            'id': id,
            'title': title,
            'photos': photo,
            'categories': None,
            'serving': '',
            'cooking_time': '',
            'kilocalories': '',
            }]
        return self.get_inline_result()

     
    def get_nav_photo(self):
        count_photo = db.sql(f'''SELECT COUNT(dish_id) as count_photos FROM photos WHERE dish_id = {self.callback_data['id']}''')[0]['count_photos']
        
        if count_photo > 1:

            buttons_ph = []
            current_num_ph = self.callback_data['num_ph']
            callback_data = copy.deepcopy(self.callback_data)

            for num_ph in range(count_photo):
                callback_data.update({'num_ph': num_ph})

                decorations = '╿' if current_num_ph == num_ph else ''

                button = InlineKeyboardButton(text=f'{decorations}{num_ph + 1}{decorations}', 
                            callback_data = set_photo_call_menu.new(**callback_data))

                if count_photo > 5:
                    if not count_photo == current_num_ph + 1:
                        max_last_btns = 2 if current_num_ph + 2 < count_photo else int(count_photo - current_num_ph +  1)
                    else:
                        max_last_btns = 4
                    max_next_btns = 2

                    if current_num_ph == num_ph:
                        buttons_ph.append(button)

                    elif num_ph >= current_num_ph - max_last_btns and num_ph <= current_num_ph + max_next_btns:
                        buttons_ph.append(button)

                    elif current_num_ph <= 2 and num_ph < 5:
                        buttons_ph.append(button)
                
                else:
                    buttons_ph.append(button)

                

        
            return buttons_ph
        return

    def get_fav_button(self):
        is_fav = self.dishe_id in self.get_favourites_user()
        if is_fav:
            text='♥️ Убрать из избранного'
        else:
            text = '🤍 В избранное'

        return InlineKeyboardButton(text=text,
            callback_data=edit_fav_by_id_call_menu.new(**self.callback_data))


    def get_post_data_by_id(self):
        try:
            self.dishe_data = self.get_by_id()[0]
        except Exception as ex:
            log(f'get_post_data_by_id exception: {ex} | user_id: {self.user_id} | query: {self.query} | dishe_id: {self.dishe_id}')
            answer = get_home_page(user_id=self.user_id, btn_title='ПОИСК ПО НАЗВАНИЮ', btn_search=self.query, add_title_row='Что-то пошло не так, воспользуйтесь поиском')
            return {
                'text': answer['text'],
                'reply_markup': answer['reply_markup'],
            }
        
        self.dishe_data.update(
            {
                'preview': 
                (MEDIA_URL + self.dishe_data['photos'].split(br)[self.callback_data['num_ph']])
                if self.dishe_data['photos'] else 
                None
            }
        )

        post_url = f'{BOT_URL}?start=get_id={self.dishe_id}'
        lines = [
            hide_link(self.dishe_data['preview']),
            hlink(self.dishe_data['title'].upper(), post_url),
            self.get_inline_description(self.dishe_data),
            hcode(f'*калорийность для сырых продуктов') + br,
            self.dishe_data['ingredients'] + br,
            f'''🧾 Как готовить:{br}{self.dishe_data['recipe'].replace(br, br*2)}''',
            br,
            hlink(f'📖 КНИГА РЕЦЕПТОВ - лучший кулинарный бот', post_url),
        ]
        message_text = br.join(lines)


        photos = self.get_nav_photo()
        fav = self.get_fav_button()
        home = get_home_button(text='🏡 На главную')
        query = get_back_to_inline(query_text=(self.query if self.query else ''))
        
        markup = InlineKeyboardMarkup(row_width=8)
        if photos and len(photos):
            markup.add(*photos)
        markup.add(fav)
        markup.add(home, query)

        return {
            'text': message_text,
            'reply_markup': markup,
        }

    async def send_post_by_id(self, message):
        
        if type(message) == types.Message:
            answer = await message.answer(parse_mode=self.parse_mode, disable_notification= self.disable_notification, **self.get_post_data_by_id())
            await message.delete()
            await update_last_message(message, castom_message_id=answer.message_id)

        elif type(message) == types.CallbackQuery:

            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=message.message.message_id,
                parse_mode=self.parse_mode,
                **self.get_post_data_by_id(),
            )

        return




async def send_inline_result(query: types.InlineQuery, get_by_query=False, get_by_category=False, get_by_favorites=False):
    user = query.from_user

    max_items = 50
    offset = int(query.offset or 0)
    stop = max_items if offset else max_items - 1
    start = (offset * stop - 1) if offset else 0

    dishes = Dishes(user_id=user.id, query=query.query, start=start, stop=stop, get_by_query=get_by_query, get_by_category=get_by_category, get_by_favorites=get_by_favorites)
    answer = dishes.get_inline_result()

    if not answer:
        answer = dishes.get_blank_inline_result()

    if len(answer) >= stop:
        next_offset = offset + 1
    else:
        next_offset = None


    answer_data = {
        'results':answer[:50],
        'cache_time': 1,
        # 'cache_time': 1,
        'is_personal': filters['favorites'] in query.query.lower(),
        'next_offset': next_offset,
    }

    await query.answer(
            **answer_data
        )
    dishes.print_all_time('Inline')


def get_parameters(query: str):
    answer = {}

    for param in query.split(LINK_SEPARATOR):
        try:
            try:
                param, value = param.split('=', 1)
            except ValueError:
                if not '/start' in param:
                    log(f'get_parameters ValueError. param={param} | query={query}')
                continue
            answer.update({f'{param}': value})
        except Exception as ex:
            log(f'get_parameters Exception {ex}. param={param} | query={query}')
    return answer





def register_user(data):
    sql_query = f'''INSERT INTO `users`(
        `user_id`, 
        `first_name`, 
        `last_name`, 
        `full_name`, 
        `is_premium`, 
        `is_bot`, 
        `language_code`, 
        `language`, 
        `language_name`, 
        `mention`,
        `url`, 
        `username`) VALUES
        (
            {data.from_user.id},
            "{data.from_user.first_name}",
            "{data.from_user.last_name}",
            "{data.from_user.full_name}",
            {bool(data.from_user.is_premium)},
            {bool(data.from_user.is_bot)},
            "{data.from_user.language_code}",
            "{data.from_user.locale.language}",
            "{data.from_user.locale.language_name}",
            "{data.from_user.mention}",
            "{data.from_user.url}",
            "{data.from_user.username}"
        )'''
    is_add = db.sql(sql_query, commit=True)
    try:
        if is_add:
            return True
        else:
            return False
    except:
        return False


async def check_start_photo(message: types.Message, user):
    try:
        is_start_photo = bool(db.sql(f'''SELECT COUNT(*) as count FROM `start_messages` WHERE user_id = {user.id}''')[0]['count'])
        if not is_start_photo:
            photo = await message.answer_photo(
                photo='https://obertivanie.com/bot_images/default/sub_to_group.png',
                protect_content=True,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'👩‍👦‍👦⠀В группу⠀👨‍👩‍👧', url='https://t.me/+aIOTdrZd3504NGUy'))
            )
            await asyncio.sleep(0.5)
            await bot.pin_chat_message(chat_id=user.id, message_id=photo.message_id)
            db.sql(f'''INSERT INTO `start_messages`(`user_id`, `message_id`) VALUES ({user.id},{photo.message_id})''')
    except:
        pass

async def start_from(came_from, user, data, *args, **kwargs) -> dict:
    last_from = db.sql(f'''SELECT came_from FROM `users` WHERE user_id = {user.id}''')[0]

    if last_from['came_from'] == came_from and came_from.isdigit():
        data.update(
            {
                'text': f'''{data['text']}{br*2}❗️ Вы уже были приглашены этим пользователем''',
            }
        )
        return data
    elif came_from == str(user.id):
        data.update(
            {
                'text':f'''{data['text']}{br*2}❗️ Вы не можете пригласить сами себя''',
            }
        )
        return data

    try:
        if not last_from['came_from'] or not last_from['came_from'].isdigit():
            sql_query = f'''UPDATE `users` SET `came_from`='{came_from}' WHERE `user_id` = {user.id}'''
            db.sql(sql_query, commit=True)
            if DEBUG:
                data.update({
                        'add_title_row': data.get('add_title_row', '') + f'⭕️ DEBUG | came_from: {came_from}{br}',
                    })

    except Exception as ex:
        log(f'start_from exception: {ex} | came_from={came_from}, user={user}, data = {data}')

    return data

async def start_gcategory(category, user, data, *args, **kwargs) -> dict:
    try:
        cat_data = db.sql(f'''SELECT * FROM search_link WHERE query = "{category}"''')

        if cat_data and not data.get('is_send', False):
            data.update({
                    'btn_title': cat_data[0]['btn_title'],
                    'btn_search': cat_data[0]['btn_search'],
                    'add_title_row': data.get('add_title_row', '') + br + cat_data[0]['description'] + br,
                })
    except Exception as ex:
        log(f'start_gcategory: {ex}, user={user}, data={data}')

    return data

async def start_get_id(dishe_id, user, message: types.Message, data,  *args, **kwargs):
    dishe = Dishes(user_id=user.id, dishe_id=int(dishe_id))
    dishe.get_by_id()
    await dishe.send_post_by_id(message=message)

    data.update({'is_send': True, })
    return data

async def start(message: types.Message):
    register_user(message)
    user = message.from_user
    data = {}
    
    await check_start_photo(message, user)

    try:
        start_params = get_parameters(message.text.replace('/start ', ''))
        for param in start_params:
            try:
                data = await globals()['start_'+ param](start_params[param], user=user, data=data, message=message)
            except Exception as ex:
                log(f'start start_params exeption: {ex}. param: {param}')

        if not data.get('is_send', False):
            message_data = get_home_page(
                user.id,
                btn_title=data.get('btn_title', None),
                btn_search=data.get('btn_search', None),
                add_title_row=data.get('add_title_row', None),
            )

            answer = await message.answer(**message_data)
            await message.delete()
            await update_last_message(message, castom_message_id=answer.message_id)
    except Exception as ex:
        log(f'start: {ex}')



def get_date() -> str:
    now = datetime.now()
    return f'{now.year}-{now.month}-{now.day}'

def user_activity_record(user_id: int, dish_id: int, query_text: str):
    sql_query = f'''
    INSERT INTO users_actions (user_id, dish_id, query_text) 
    VALUES 
    ({user_id},{dish_id},"{query_text}")
    '''
    db.sql(sql_query, commit=True)

async def check_activity(message: types.Message):
    user = message.from_user

    today_activity = db.sql(f'''
        SELECT COUNT(*) as `count`
        FROM `users_actions` 
        WHERE `dish_id` = `query_text` AND user_id = {user.id} AND time_at = "{get_date()}";'''
    )[0]['count']


    if today_activity > 50 and not user.id == ADMIN_ID:
        answer_id = await message.answer(
            text=f'''Вы слишком активны. Попробуйте завтра.{br}Вы все еще можете использовать другие возможности бота.{br*2}В главное меню - /start{br*2}{hlink('Связь с администратором', BUY_AD_URL)}''',
            parse_mode='html',
        )
        await message.delete()
        await update_last_message(message, castom_message_id=answer_id.message_id)

        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f'Слишком активный пользователь{br}user_id={user.id}{br}Активность: {today_activity}',
            parse_mode='html',
        )
        return False

    text = message.text
    if text.isdigit() and not user.id == ADMIN_ID:
        user_activity_record(user_id=user.id, dish_id=int(text), query_text=text)
    return True









async def dont_get_you(message: types.Message):
    answer = await message.answer(
        text='Прости, но я тебя не понял.',
        reply_markup=InlineKeyboardMarkup().add(get_home_button('🫤 На главную 🥲')),
    )
    await message.delete()
    await update_last_message(message, castom_message_id=answer.message_id)


















































