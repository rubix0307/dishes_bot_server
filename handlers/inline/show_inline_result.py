
import os
import time

from aiogram import types
import requests
from app import dp
from config import MEDIA_URL
from functions import (get_blank_data, get_data_by_category, get_data_by_favorites, get_data_by_mailing, get_data_by_query_text,
                       get_inline_result, get_normal_form,
                       сleaning_input_text_for_search, сleaning_input_text_from_sql_injection)
from markups import br, filters

@dp.inline_handler()
async def main(query: types.InlineQuery):
    start_time = time.time()

    query.query = сleaning_input_text_from_sql_injection(query.query)


    max_items = 45
    offset = int(query.offset or 0)
    max_dishes = max_items if offset else max_items - 1
    start = (offset * max_dishes - 1) if offset else 0

    data = {
        'query': query,
        'user_id': query.from_user.id,
        'query_text': get_normal_form(query.query),
        'max_dishes': max_dishes,
        'offset': offset,
        'start': start,
        'is_personal_chat': True if query._values['chat_type'] == 'private' else False,
    }

    if filters['favorites'] in query.query.lower():
        data_list = get_data_by_favorites(**data)

    elif filters['category'] in query.query:
        data_list = get_data_by_category(**data)

    elif filters['mailing'] in query.query:
        data_list = get_data_by_mailing(**data)

    else:
        data_list = get_data_by_query_text(**data)


    if not data_list:
        data_list = get_blank_data(id=0)
        query.query = ''

    if len(data_list) >= max_dishes:
        next_offset = offset + 1
    else:
        next_offset = None

        if not get_blank_data(id=0)[0] in data_list and (len(data_list) > 8 or offset):
            data_list.append(get_blank_data(
                id=-100,
                title='Ты долистал до конца',
                photo='default/the_end.png')[0],
            )

    data.update({'data_list': data_list[:50]})

    answer = get_inline_result(**data)

    open(f'current_urls.txt', 'w').write(f'{query.query}{br}')
    for a in answer:
        open(f'current_urls.txt', 'a').write(f'{a.thumb_url}{br}')


    get_data = time.time()

            


    get_fav: bool = filters['favorites'] in query.query.lower()
    answer_data = {
        'results':answer[:50],
        # 'cache_time': 1 if get_fav or data['is_personal_chat'] or filters['mailing'] in query.query else 60*10,
        'cache_time': 1,
        'is_personal': get_fav,
        'next_offset': next_offset,
    }

    if data['is_personal_chat']:
        answer_data.update({
            'switch_pm_text':'Ускорить поиск',
            'switch_pm_parameter':'speed',
        })

    

    await query.answer(
            **answer_data
        )

    query_answer_time_end = time.time()
    print(f'| text   | {data["query_text"]}')
    print(f'| chat   | {query._values["chat_type"]}')
    print(f'| inline | get in {round(get_data - start_time, 3)}s')
    print(f'| inline | all in {round(query_answer_time_end - start_time, 3)}s', end=br*2)
