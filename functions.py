import copy
import datetime
import re
import time

import pymorphy2
from aiogram import Bot, types
from aiogram.dispatcher import FSMContext
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.markdown import *

from app import bot
from config import ADMIN_ID, BOT_URL, BUY_AD_URL, MEDIA_URL
from db.functions import (get_categories_data_from_id, get_fav_dish_by_user,
                          get_ingredients_data_from_id,
                          get_photos_data_from_id, sql)
from markups import *


def get_user_role(user_id) -> int:
        user_role = sql(f'SELECT `role_id` FROM `users` WHERE `user_id` = {user_id}')
        if user_role:
            return user_role[0]['role_id']
        else:
            return 1


async def check_start_photo(user_id):
    try:
        is_start_photo = bool(sql(f'''SELECT COUNT(*) as count FROM `start_messages` WHERE user_id = {user_id}''')[0]['count'])
        if not is_start_photo:
                photo = await bot.send_photo(chat_id=user_id, photo='https://obertivanie.com/bot_images/default/panda_sub.png', protect_content=True,
                    reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(
                        text=f'👩‍👦‍👦⠀В группу⠀👨‍👩‍👧', 
                        url='https://t.me/+aIOTdrZd3504NGUy'))
                    )

                time.sleep(0.2)
                await bot.pin_chat_message(chat_id=user_id, message_id=photo.message_id)
                sql(f'''INSERT INTO `start_messages`(`user_id`, `message_id`) VALUES ({user_id},{photo.message_id})''')
    except:
        pass

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
        'markup': markup,
        'parse_mode': 'html',
    }

def сleaning_input_text_from_sql_injection(text: str):

    sumbols = '|'.join('~!@#$%*()+:;<>,.?/^')
    answer = re.sub(f'[|{sumbols}|]','',text).replace('  ', ' ').strip()
    return answer


def сleaning_input_text_for_search(query_text: str):
    query_text = f' {query_text} '
    prelogs = [' без ', ' безо ', ' близ ', ' в ',  ' во ', ' вместо ', ' вне ', ' для ', ' до ', ' за ', ' из ', ' изо ', ' к ',  ' ко ', ' кроме ', ' между ', ' меж ', ' на ', ' над ', ' надо ', ' о ',  ' об ', ' обо ', ' от ', ' ото ', ' перед ', ' передо ', ' предо ', ' пo ', ' под ', ' при ', ' про ', ' ради ', ' с ',  ' со ', ' сквозь ', ' среди ', ' через ', ' чрез ']
    for prelog in prelogs:
        query_text = query_text.replace(prelog, ' ')

    return query_text.strip()

def get_advertisement(id: int, offset: int, query_text: str) -> types.InlineQueryResultArticle:

    data_ad = sql(f'SELECT * FROM ads WHERE position = {id} AND offset = {offset}')

    if data_ad:
        data_ad = data_ad[0]

        

        input_message_content=types.InputTextMessageContent(
                message_text=f'''{hide_link(MEDIA_URL + data_ad['preview_photo'])}{data_ad['message_text']}'''+ f'''\n{'-'*40}\n{hlink(f'Заказать рекламу в боте', BUY_AD_URL)}''',
                parse_mode=data_ad['parse_mode'])
        

        markup = InlineKeyboardMarkup()
        
        url_button = InlineKeyboardButton(text=data_ad['url_button_text'] , url=data_ad['url'])

       

        markup.add(url_button)
        markup.add(get_home_button(text='🏡 На главную'), get_back_to_inline(query_text=query_text))

        if not data_ad['preview_photo']:
            data_ad['preview_photo'] = 'default/404.png'

        result_article = {
            'id': id*-1,
            'title':  data_ad['preview_title'],
            'url':  data_ad['url'],
            'thumb_url':  MEDIA_URL + data_ad['preview_photo'],
            'description':  data_ad['preview_description'],
            'input_message_content': input_message_content,
            'reply_markup': markup,
        }



    else:
        input_message_content=types.InputTextMessageContent(
                message_text=f'''Реклама №{id}{br}{f'Страница №{offset+1}'}{br*2}{hlink(f'📖 Книга рецептов', BOT_URL)}''',
                parse_mode='html')

        result_article = {
            'id': id*-1,
            'title': f'‼️ Ваша реклама ‼️',
            'thumb_url': MEDIA_URL + f'default/your_ad.png',
            'description': f'№ стр:{offset + 1} №{id} | Заказать рекламу можно тут',
            'input_message_content': input_message_content,
            'reply_markup': InlineKeyboardMarkup().add(get_home_button()) 

        }
        

    return types.InlineQueryResultArticle(
        **result_article,   
        )

def insert_ad(offset, answer, query_text):

    for round, i in enumerate(range(0, len(answer) + 1, 10)):
        answer.insert(i, get_advertisement(round + 1, offset, query_text))
    
    return answer

class Article:

    def __init__(self, data, callback_data=None, user_id=0, is_mailing=False):
        self.id = data['id']
        self.title = data['title']  
        self.serving = data['serving']
        self.cooking_time = data['cooking_time']
        self.kilocalories = data['kilocalories']
        self.protein = data['protein']
        self.fats = data['fats']
        self.carbohydrates = data['carbohydrates']
        self.recipe = data['recipe'] if data['recipe'] else ''

        self.categories = data['categories'].capitalize() if data['categories'] else ''
        self.ingredients = data['ingredients']


        if callback_data:
            self.callback_data = callback_data
        else:
            self.callback_data = {
                'id': data['id'],
                'fav': int(data['id'] in get_fav_ids(user_id)),
                'query': '',
                'num_ph': 0,
            }
        try:
            self.preview = data['photos'].split('\n')[callback_data['num_ph']]
        except:
            self.preview = edit_preview(call_data=self.callback_data, next_photo=False, get_url=True)

        

        self.is_mailing = is_mailing
        self.user_id = user_id
        self.data = data


    def get_description(self):
        return f'Порций: {self.serving} | {self.cooking_time} | {self.kilocalories} ккал{br}{self.categories}' if self.id > 0 else '😢'

    def get_message_text(self, show_preview: bool = True, is_send_instagram=False):

        if not MEDIA_URL in self.preview:
            self.preview = MEDIA_URL + self.preview

        

        if not is_send_instagram:
            lines = [
                hide_link(self.preview) if show_preview else '',
                hlink(self.title.upper(), f'{BOT_URL}?start=get_id={self.id}'),
                self.get_description(),
                hcode(f'*калорийность для сырых продуктов') + br,
                self.ingredients + br,
                f'🧾 Как готовить:{br}{self.recipe}' if not self.is_mailing else f'',
                br,
                hlink(f'📖 КНИГА РЕЦЕПТОВ - лучший кулинарный бот', f'{BOT_URL}?start=get_id={self.id}'),
            ]
        else:
            lines = [
                self.title,
                self.get_description(),
                br,
                self.ingredients,
                br,
                '📌 Этот и другие рецепты смотрите в шапке профиля'
            ]

        
        message_text = br.join(lines)
        return message_text if self.id > 0 else 'Похоже, тут ничего не найдено'



        
    def get_markup(self, clear_query=False):
        
        markup = InlineKeyboardMarkup(row_width=8)
        
        if self.is_mailing:
            markup.add(InlineKeyboardButton(
                text='Смотерть в боте',
                url=BOT_URL + f'?start=get_id={self.id}',
            ))
            return markup


        home = get_home_button(text='🏡 На главную')
        query = get_back_to_inline(query_text=(self.callback_data['query'] if not clear_query else ''))

        if not self.callback_data['id'] < 1:
            try:
                photos = self.get_nav_photo()
                markup.add(*photos)

            except Exception as e:
                try:
                    self.callback_data['query'] = ''
                    photos = self.get_nav_photo()
                    markup.add(*photos)
                except TypeError:
                    pass

            

            try:
                fav = self.get_fav_button()
                markup.add(fav)
            except Exception as e:
                print()

            

            
            markup.add(home, query)


            # admin mailing
            # if get_user_role(self.user_id) == 2:
            #     try:
            #         markup.add(*self.get_mailing_buttons())
            #     except:
            #         pass


        else:
            markup.add(home, query)
        
        return markup
    
    def get_nav_photo(self):
        count_photo = sql(f'''SELECT COUNT(dish_id) as count_photos FROM photos WHERE dish_id = {self.callback_data['id']}''')[0]['count_photos']
        
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

        if self.callback_data['fav']:
            text='♥️ Убрать из избранного'
        else:
            text = '🤍 В избранное'

        return InlineKeyboardButton(text=text,
            callback_data=edit_fav_by_id_call_menu.new(**self.callback_data))
        
    def get_mailing_buttons(self):
        try:

            all_mailing_dishe = sql(f'SELECT DISTINCT view FROM mailing WHERE dish_id = {self.id}')
            all_count_mails = sql(f'SELECT COUNT(*) as count FROM `mailing`')[0]['count']

            data_mailing = {'text': f'✅ Добавить в рассылку ({all_count_mails})',
                            'callback_data': mailing.new(
                                dish_id=self.id, 
                                add=1,
                                query_text=self.callback_data['query']
                                )
                            } 

            if all_mailing_dishe:
                view = all_mailing_dishe[0]['view']
                if not view:
                    data_mailing = {'text': f'🛑 Убрать из рассылки ({all_count_mails})',
                                    'callback_data': mailing.new(
                                        dish_id=self.id,
                                        add=0,
                                        query_text=self.callback_data['query']
                                        )
                                    }
                
            send_now = InlineKeyboardButton('🆕 Отправить сейчас', callback_data=mail_now.new(dish_id=self.id))
            add_in_mailing = InlineKeyboardButton(**data_mailing)
            return [add_in_mailing, send_now]
                
        except:
            pass

    def get_inline_query_result(self) -> types.InlineQueryResultArticle:
        return types.InlineQueryResultArticle(
            reply_markup = self.get_markup(),
            input_message_content = types.InputTextMessageContent(
                    message_text= self.get_message_text(),
                    parse_mode='html',
                ),
            

            id= self.id,
            title= self.title,
            thumb_url= MEDIA_URL + self.preview,
            description= self.get_description(),
        
        )





def get_inline_result(query, data_list, offset, is_personal_chat: bool = False, query_text: str = '', **kwargs):
    answer = []

    if not is_personal_chat:
        for data in data_list:

            if data['id'] > 0:
                if not data['categories']:
                    data['categories'] = "-"*20

                description = f'''Порций: {data['serving']} | {data['cooking_time']} | {data['kilocalories']} ккал{br}{data['categories'].capitalize()}'''
            else:
                description = f'😢'

            try:

                thumb_url = data['photos'].split('\n')[0] if type(data['photos']) == str else (data['photos'][0] if data['photos'] else None)
                if not thumb_url:
                    thumb_url = 'default/404.png'
                
                
                answer.append(
                    types.InlineQueryResultArticle(
                        input_message_content = types.InputTextMessageContent(
                                message_text= f"get_id={data['id']}&query_text={query_text}",
                                parse_mode='html',
                            ),
                        

                        id= data['id'],
                        title= data['title'],
                        thumb_url= MEDIA_URL + thumb_url,
                        description= description,
                    
                    )
                )
            except:
                pass



    else:
        fav_ids = get_fav_ids(query.from_user.id)
        for item in data_list:
            try:

                callback_data = {
                    'id': item['id'],
                    'fav': 1 if item['id'] in fav_ids else 0,
                    'query': query.query,
                    'num_ph': 0,
                }
                answer.append(Article(item, callback_data).get_inline_query_result())
            except Exception as ex:
                continue

    # ad block
    # insert_ad(offset, answer, query.query)
    
    
    return answer

def get_extra_data(data_list):

    remove_list = []
    for round, data in enumerate(data_list):
        try:
            categories = get_categories_data_from_id(data['id'])
            ingredients = get_ingredients_data_from_id(data['id'])
            photos = get_photos_data_from_id(data['id'])
            new = {
                'categories': categories,
                'ingredients': ingredients,
                'photos': photos,
                }

            data_list[round].update(new)
        except:
            remove_list.append(data)
            continue

    for i in remove_list:
        data_list.remove(i)

    return data_list




def get_blank_data(id=-1, title='К сожалению, ничего не найдено', photo='default/404.png'):
    data_list = [{
            'id': int(id),
            'title':title,
            'link':' ',
            'photo':photo,
            'category':' ',
            'count_ingredients':' ',
            'serving':' ',
            'cooking_time':' ',
            'kilocalories':0,
            'protein':0,
            'fats':0,
            'carbohydrates':0,
            'ingredients':'',
            'list_ingredients':'',
            'recipe':' ',
            'rating':0,
            'categories': [],
            'ingredients': [],
            'photos': [photo],
            'preview': photo,
            'likes': 0,
        }]
    return data_list


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

    last_message = sql(f'SELECT message_id FROM users_messages WHERE user_id = {user["id"]}')
    
    if not len(last_message):
        sql(f'INSERT INTO `users_messages`(`user_id`, `message_id`) VALUES ({user["id"]},{message_id})', commit=True)
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
            sql(f'UPDATE users_messages SET message_id={message_id} WHERE user_id = {user["id"]}', commit=True)


def get_call_data(callback_data: dict) -> dict:
    # use base_markup_menu
    return {
        'id': int(callback_data.get('id')),
        'fav': int(callback_data.get('fav')),
        'query': callback_data.get('query'),
        'num_ph': int(callback_data.get('num_ph')),
    }

def get_fav_ids(user_id: int) -> list:

    fav = get_fav_dish_by_user(user_id)
    fav = fav if fav else []
    fav_ids = [item['id'] for item in fav]

    return fav_ids













def get_alphabet_sort(sorting_list: list):
    for letter_number in range(min([len(i) for i in sorting_list])):

        for round in range(len(sorting_list)):
            for i in range(len(sorting_list) - 1):

                if not letter_number:
                    if ord(sorting_list[round][letter_number]) < ord(sorting_list[i][letter_number]):
                        sorting_list[round], sorting_list[i] = sorting_list[i], sorting_list[round]
                else:
                    if ord(sorting_list[round][letter_number]) < ord(sorting_list[i][letter_number]) and ord(sorting_list[round][0]) == ord(sorting_list[i][0]):
                        sorting_list[round], sorting_list[i] = sorting_list[i], sorting_list[round]
    return sorting_list




def edit_preview(article=None, call_data=None, next_photo=False, get_url=False):
    
        photos = sql(f'''SELECT local_photo FROM photos WHERE dish_id = {call_data['id']}''')

        if next_photo:
            call_data['num_ph'] += 1
        
        try:
            url = MEDIA_URL + photos[call_data['num_ph']]['local_photo']
        except:
            try:
                call_data['num_ph'] = 0
                url = MEDIA_URL + photos[0]['local_photo']
            except IndexError:
                url = None



        if not get_url:
            article.preview = url
            return article, call_data

        else:
            return url






def get_data_dish(id: int):
    if id > 0:
        sql_query = f'''
        SELECT SQL_CACHE  d.id, d.title, d.original_link, d.serving, d.cooking_time, d.kilocalories,d.protein, d.fats, d.carbohydrates, d.recipe, d.likes,
            (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
            (select GROUP_CONCAT(p.local_photo SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos,
            (select GROUP_CONCAT(DISTINCT CONCAT(i.title,": ", di.value) SEPARATOR '\n') from ingredients as i 
            INNER JOIN dishes_ingredients as di ON di.ingredient_id = i.id where di.dish_id=d.id
            ) as ingredients
        
        FROM dishes as d

        WHERE d.id = {id}
        '''
        answer = sql(sql_query)[0]
        return answer
    else:
        return get_blank_data(id=id)[0]









def get_by_favorites(user_id, start, max_dishes):

    sql_query = f'''
    SELECT d.*,
        (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
        (select GROUP_CONCAT(p.local_photo SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos,
        (select GROUP_CONCAT(DISTINCT CONCAT(i.title,": ", di.value) SEPARATOR '\n') from ingredients as i INNER JOIN dishes_ingredients as di ON di.ingredient_id = i.id where di.dish_id=d.id) as ingredients
    FROM dishes as d

    INNER JOIN fav_dish_user as fdu ON fdu.user_id = {user_id} AND fdu.dish_id = d.id
    WHERE 1
    LIMIT {start},{max_dishes}'''
    data_list = sql(sql_query)

    return data_list

def get_by_favorites_min(user_id, start, max_dishes):
    sql_query = f'''
    SELECT d.id, d.title, d.serving, d.cooking_time, d.kilocalories, 
        (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
        (select p.local_photo from photos as p where p.dish_id=d.id limit 1) as photos
    FROM dishes as d 
    WHERE d.id in (select dish_id from fav_dish_user where user_id = {user_id})
    ORDER BY d.likes DESC
    LIMIT {start},{max_dishes}
    '''
    data_list = sql(sql_query)
    return data_list

def get_data_by_favorites(user_id, start, max_dishes, is_personal_chat: bool = False, **kwargs):
    
    if not is_personal_chat:
        data_list = get_by_favorites_min(user_id, start, max_dishes)
    else:
        data_list = get_by_favorites(user_id, start, max_dishes)
    return data_list



def get_by_category(category_id, start, max_dishes):

    sql_query = f'''
        SELECT SQL_CACHE  d.*,
            (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
            (select GROUP_CONCAT(p.local_photo SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos,
            (select GROUP_CONCAT(DISTINCT CONCAT(i.title,": ", di.value) SEPARATOR '\n') from ingredients as i INNER JOIN dishes_ingredients as di ON di.ingredient_id = i.id where di.dish_id=d.id) as ingredients
        FROM dishes as d

        LEFT JOIN dishes_categories as dc ON dc.dish_id = d.id
        LEFT JOIN categories as c ON c.id = dc.category_id
       
        WHERE dc.category_id = {category_id} 
        
        ORDER BY d.likes
        LIMIT {start},{max_dishes}
    '''

    data_list = sql(sql_query)

    return data_list

def get_by_category_min(category_id, start, max_dishes):

    sql_query = f'''
        SELECT SQL_CACHE d.id, d.title, d.serving, d.cooking_time, d.kilocalories, 
            (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
            (select p.local_photo from photos as p where p.dish_id=d.id limit 1) as photos
        FROM dishes as d 
        WHERE d.id in (select dish_id from dishes_categories where category_id = {category_id})
        ORDER BY d.likes DESC
        LIMIT {start},{max_dishes}
    '''

    data_list = sql(sql_query)

    return data_list

def get_data_by_category(query, start, max_dishes, is_personal_chat: bool = False, **kwargs):

    cat_name = query.query.split(filters['category'])[1]

    try:
        category_id = sql(
            f'SELECT SQL_CACHE id FROM categories WHERE title LIKE "{cat_name}%" LIMIT 1')[0]['id']
    except IndexError:
        category_id = 27


    if not is_personal_chat:
        data_list = get_by_category_min(category_id, start, max_dishes)
    else:
        data_list = get_by_category(category_id, start, max_dishes)
    return data_list


def get_data_by_mailing(start, max_dishes,  **kwargs):
    sql_query = f'''
        SELECT SQL_CACHE 
        d.id, d.title, d.serving, d.cooking_time, d.kilocalories, 
        (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
        (select p.local_photo from photos as p where p.dish_id=d.id limit 1) as photos
                
        FROM dishes as d 
        WHERE d.id in (select dish_id from mailing where view = 0)
        ORDER BY d.likes DESC
        LIMIT {start},{max_dishes}
        '''
    return sql(sql_query)

def get_by_query_text(query_text, start, max_dishes):

    data_list = sql(
        f'''SELECT SQL_CACHE d.*,
                (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                (select GROUP_CONCAT(p.local_photo SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos,
                (select GROUP_CONCAT(DISTINCT CONCAT(i.title,": ", di.value) SEPARATOR '\n') from ingredients as i INNER JOIN dishes_ingredients as di ON di.ingredient_id = i.id where di.dish_id=d.id) as ingredients
        FROM dishes as d
        WHERE MATCH (d.norm_title, d.title) AGAINST ("{query_text}") LIMIT {start},{max_dishes}''')
    if not data_list:
        data_list = sql(
            f'''SELECT SQL_CACHE d.*,
                (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                (select GROUP_CONCAT(p.local_photo SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos,
                (select  GROUP_CONCAT(DISTINCT CONCAT(i.title,": " ,di.value)) from ingredients as i INNER JOIN dishes_ingredients as di ON di.ingredient_id = i.id where di.dish_id=d.id) as ingredients

            FROM dishes as d
            WHERE d.norm_title LIKE "%{query_text}%" ORDER BY d.likes LIMIT {start},{max_dishes}''')
    
    return data_list

def get_by_query_text_min(query_text, start, max_dishes):
    data_list = sql(
            f'''SELECT  SQL_CACHE d.id, d.title, d.serving, d.cooking_time, d.kilocalories, 
                (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                (select GROUP_CONCAT(p.local_photo SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos
            FROM dishes as d 

            WHERE MATCH (d.norm_title, d.title) AGAINST ("{query_text}")
            LIMIT {start}, {max_dishes}'''
        )
    if not data_list:
        data_list = sql(
            f'''
            SELECT SQL_CACHE  d.id, d.title, d.serving, d.cooking_time, d.kilocalories,
                (select GROUP_CONCAT(c.title SEPARATOR ', ') from categories as c INNER JOIN dishes_categories as dc ON c.id=dc.category_id where dc.dish_id=d.id) as categories,
                (select GROUP_CONCAT(p.local_photo SEPARATOR '\n') from photos as p where p.dish_id=d.id) as photos
            FROM dishes as d 
            WHERE norm_title LIKE "%{query_text}%"
            LIMIT {start},{max_dishes}
            ''')
    return data_list

def get_data_by_query_text(search_text, start, max_dishes, is_personal_chat: bool = False, **kwargs):
    
    if not is_personal_chat:
        data_list = get_by_query_text_min(search_text, start, max_dishes)
    else:
        data_list = get_by_query_text(search_text, start, max_dishes)
    return data_list







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
    is_add = sql(sql_query, commit=True)
    try:
        if is_add:
            return True
        else:
            return False
    except:
        return False





def get_mailing_data(castom_dish_id: int = None):
    try:

        if not castom_dish_id:
            mailing_ids = sql(f'SELECT * FROM `mailing` WHERE not view ')
            sql(f'''DELETE FROM mailing WHERE id = {mailing_ids[0]['id']}''', commit=True)

                

            dish_id = mailing_ids[0]['dish_id']
            
        else:
            dish_id = castom_dish_id

        call_data = {
                        'id': dish_id,
                        'fav': 0,
                        'query': ' ',
                        'num_ph': 0,
                        }

        data = get_data_dish(dish_id)
        article = Article(data, callback_data=call_data, is_mailing=True)

        try:
            return article, len(mailing_ids)
        except:
            return article, -1
    except:
        pass



def get_activity(user):
    today_activity = sql(f'''
        SELECT COUNT(*) as `count` FROM `users_actions` 
        WHERE user_id = {user.id} AND time_at = "{get_date()}";''')
    count_activity = today_activity[0]['count']
    return count_activity

def user_activity_record(user_id: int, dish_id: int, query_text: str):
    sql_query = f'''
    INSERT INTO users_actions (user_id, dish_id, query_text) 
    VALUES 
    ({user_id},{dish_id},"{query_text}")
    '''
    sql(sql_query, commit=True)



morph = pymorphy2.MorphAnalyzer()
def get_normal_form(text: str):
    global morph
    
    text = text.replace('(', '').replace(')', '').replace('\'', '')

    prelogs = [' без ', ' безо ', ' близ ', ' в ',  ' во ', ' вместо ', ' вне ', ' для ', ' до ', ' за ', ' из ', ' изо ', ' и ', ' к ',  ' ко ', ' кроме ', ' между ', ' меж ', ' на ', ' над ', ' надо ', ' о ',  ' об ', ' обо ', ' от ', ' ото ', ' перед ', ' передо ', ' предо ', ' пo ', ' под ', ' при ', ' про ', ' ради ', ' с ',  ' со ', ' сквозь ', ' среди ', ' через ', ' чрез ']
    for sumb in prelogs:
        text = text.replace(sumb, ' ')

    normal_form = [morph.parse(i)[0].normal_form for i in text.split()]

    return ' '.join(normal_form)


def get_date() -> str:
    now = datetime.datetime.now()
    return f'{now.year}-{now.month}-{now.day}'


async def you_very_active(bot: Bot, message: types.Message, count_activity: int) -> None:
    user = message.from_user
    await update_last_message(message, castom_message_id=message.message_id + 1)
    await message.delete()
    await message.answer(
        text=f'''Сегодня вы слишком активны. Попробуйте попозже{br*2}{hlink('Связь с администратором', BUY_AD_URL)}''',
        reply_markup=InlineKeyboardMarkup().add(get_home_button()),
        parse_mode='html',
        )
    await bot.send_message(chat_id=ADMIN_ID, text=f'Слишком активный пользователь {user.id} [{count_activity}]')

async def contest(message: types.Message, is_callback=False):
        user_id = message.from_user.id
        role_id = get_user_role(user_id)
        

        contest_users = sql(f'''
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
            user_activity_record(user_id, None, message.text)
            await message.delete()
        else:
            answer = await bot.send_message(chat_id = user_id, text=msg, reply_markup=markup, disable_web_page_preview=True, parse_mode='html')
            user_activity_record(user_id, None, call_filters['contest'])
        await update_last_message(message, castom_message_id = answer.message_id)
    





async def groups(message: types.Message, is_callback=False):
    user_id = message.from_user.id

    markup = InlineKeyboardMarkup(row_width=3)
    
    markup.add(InlineKeyboardButton('📖 Книга Рецептов 🔥', url='https://t.me/+aIOTdrZd3504NGUy'))
    markup.add(InlineKeyboardButton('📖 Кулинарные Лайфхаки💡', url='https://t.me/+JKomHC4hlhQ2NTNi'))
    markup.add(get_home_button('🎄 На главную 🌟'))


    if not is_callback:
        answer = await message.answer_photo(photo='https://obertivanie.com/bot_images/default/sub_to_group.png', protect_content=True,
                reply_markup=markup, parse_mode='html')
        user_activity_record(user_id, None, message.text)
        await message.delete()
    else:
        answer = await bot.send_photo(photo='https://obertivanie.com/bot_images/default/sub_to_group.png', protect_content=True, chat_id = user_id, reply_markup=markup, parse_mode='html')
        user_activity_record(user_id, None, call_filters['groups'])
    await update_last_message(message, castom_message_id = answer.message_id)


async def start(message: types.Message,state=None,):
        is_reg = register_user(message)

        user = message.from_user
        
        btn_title = None
        btn_search = None
        add_title_row = None
        show_diche = False
        query_text = ''


        data_answer = {
            'text': '',
        }
        
        try:
            is_return = False
            start_parameters = message.text.split()[1].split('__')

            for start_parameter in start_parameters:
                if start_parameter == 'speed':
                    data_answer.update({'text':f'''{data_answer['text']}{br*2}❗️ Быстрый поиск работает только в этом чате (с ботом)'''})
                
                elif 'from=' in start_parameter or start_parameter.isdigit():

                    try:
                        came_from = start_parameter.split('=')[1]
                    except IndexError:
                        came_from = start_parameter

                    last_from = sql(f'''SELECT came_from FROM `users` WHERE user_id = {user.id}''')[0]

                    if last_from['came_from'] == came_from:
                        data_answer.update({'text':f'''{data_answer['text']}{br*2}❗️ Вы уже были приглашены этим пользователем'''})
                        continue

                    elif last_from['came_from'] and last_from['came_from'].isdigit() and came_from.isdigit():
                        data_answer.update({'text':f'''{data_answer['text']}{br*2}❗️ Вы уже были приглашены другим пользователем'''})
                        continue

                    elif came_from == str(user.id):
                        data_answer.update({'text':f'''{data_answer['text']}{br*2}❗️ Вы не можете пригласить сами себя'''})
                        continue

                    try:
                        if not last_from['came_from'] or not last_from['came_from'].isdigit():
                            sql_query = f'''UPDATE `users` SET `came_from`='{came_from}' WHERE `user_id` = {user.id}'''
                            sql(sql_query, commit=True)
                            continue
                    except Exception as e:
                        pass

                elif start_parameter == call_filters['contest']:
                    await contest(message)
                    await update_last_message(message, castom_message_id = message.message_id + 1)
                    user_activity_record(user.id, None, message.text)

                    is_return = True

                elif 'gcategory=' in start_parameter:
                    cat = start_parameter.split('=')[1]
                    categories = {
                        'zavtrak':['🍳 ЗАВТРАК', 'Категория=завтраки', 'свой '],
                        'pervie':['🍲 ПЕРВЫЕ БЛЮДА', 'Категория=супы', 'вкуснейшие '],
                        'osnovnie':['🍖 ОСНОВНЫЕ БЛЮДА', 'Категория=основные', ''],
                        'obed':['🍽 НА ОБЕД', 'Категория=основные', 'что покушать '],
                        'desert':['🥞 ДЕСЕРТЫ', 'Категория=выпечка', 'невероятные '],
                    }
                    if cat in categories.keys():
                        btn_title = categories[cat][0] + ' 👩‍🍳'
                        btn_search = categories[cat][1]
                        add_title_row = f'Смотри {categories[cat][2]} {categories[cat][0]} по кнопке ниже'
                    
                elif 'get_id=' in start_parameter:
                    dish_id = int(start_parameter.split('=')[1])
                    show_diche = True

                elif 'query_text=' in start_parameter:
                    query_text = start_parameter.split('=')[1]
        
        except IndexError:
            start_parameter = None

        if is_return:
            return

        if not show_diche:
            data = get_home_page(user.id, btn_title=btn_title, btn_search=btn_search, add_title_row=add_title_row)
        else:
            data = get_data_start_get_id(user.id, dish_id, query_text)


        data_answer = {
            'text': f'''{data['text']} {data_answer['text']}''',
            'reply_markup': data['markup'],
            'parse_mode': data['parse_mode'],
        }
        

        try:
            is_start_photo = bool(sql(f'''SELECT COUNT(*) as count FROM `start_messages` WHERE user_id = {user.id}''')[0]['count'])
            if is_reg or not is_start_photo:
                    photo = await message.answer_photo(photo='https://obertivanie.com/bot_images/default/sub_to_group.png', protect_content=True,
                    reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'👩‍👦‍👦⠀В группу⠀👨‍👩‍👧', url='https://t.me/+aIOTdrZd3504NGUy')))
                    time.sleep(0.5)
                    await bot.pin_chat_message(chat_id=user.id, message_id=photo.message_id)
                    sql(f'''INSERT INTO `start_messages`(`user_id`, `message_id`) VALUES ({user.id},{photo.message_id})''')
        except:
            pass

        answer = await message.answer(**data_answer)
        await update_last_message(message, castom_message_id = answer.message_id)
        user_activity_record(user.id, 0, message.text)
        await message.delete()




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

async def by_countries(bot, call, highlight_symbol = '⭐️ '):

    text = 'Кухни разных стран'
    top_categories = sql(
        f'SELECT title, emoji FROM `categories` WHERE favorite = 1')
    categories = sql(
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
    categories = sql('SELECT title,emoji FROM categories WHERE parent_id = 2 AND is_show = 1')
    answer = {
        'parse_mode': 'html',
        'reply_markup': buttons_list_categories(categories, highlight_symbol).add(get_home_button()),
        'text': text,  
    }
    await send_categories(bot, call, answer)

async def get_home(call):
    data = get_home_page(call.from_user.id)

    message_data = {
        'text': data['text'],
        'reply_markup': data['markup'],
        'parse_mode': 'html',
    }

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


def get_data_start_get_id(user_id, dish_id, query_text):
    fav_ids = get_fav_ids(user_id)
    callback_data = {
        'id': dish_id,
        'fav': int(dish_id in fav_ids),
        'query': query_text,
        'num_ph': 0,
    }

    data = get_data_dish(dish_id)
    article = Article(data, callback_data=callback_data, user_id=user_id)
    try:
        article.preview = MEDIA_URL + data['local_photo']
    except:
        pass


    data = {
        'markup': article.get_markup(),
        'text': article.get_message_text(),
        'parse_mode': 'html',
    }
    return data











async def send_categories_markup(message: types.Message, dishe_id, state=FSMContext):



    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    dishes_categories = sql(f'''SELECT * FROM `dishes_categories` WHERE dish_id = {dishe_id};''')
    ids = ','.join([str(i['category_id']) for i in dishes_categories])
    if not ids:
        ids = '0'

    categories_active = sql(f'''SELECT * FROM `categories` WHERE id IN ({ids})''')
    categories = sql(f'''SELECT * FROM `categories` WHERE parent_id AND id NOT IN ({ids})''')
    
    for category in categories_active:
        markup.add(KeyboardButton(f'''- {category['title']} -'''))
    for category in categories[::-1]:
        markup.add(KeyboardButton(category['title']))

    answer = await message.answer('Категории', reply_markup=markup)
    async with state.proxy() as data:
        data['dishe_id'] = dishe_id
        data['category_message_id'] = answer.message_id




def is_edited_mode(user_id, state: FSMContext) -> bool:
    return state.storage.data[str(user_id)][str(user_id)]['state'] == 'EditCategories:active'











































