from aiogram import types
from app import bot, dp
from functions.db import sql
from functions.main import Dishes, user_activity_record
from functions.markups import edit_fav_by_id_call_menu, get_call_data


@dp.callback_query_handler(edit_fav_by_id_call_menu.filter(), state='*')
async def show_dish(call: types.CallbackQuery, callback_data: dict()):

    user = call.from_user
    call_data = get_call_data(callback_data)

    if not call_data['fav']:
        answer_text = 'Добавлено в избранное'
        sql(
            f'''INSERT INTO fav_dish_user (user_id, dish_id) VALUES ({user.id},{call_data['id']})''',
            commit=True,
        )
        user_activity_record(user.id, call_data['id'], 'add fav')
    else:
        answer_text = 'Убрано из избранного'
        sql(
            f'''DELETE FROM fav_dish_user WHERE fav_dish_user.user_id = {user.id} AND fav_dish_user.dish_id = {call_data['id']}''',
            commit=True,
        )
        user_activity_record(user.id, call_data['id'], 'remove fav')

    call_data['fav'] = int(not call_data['fav'])

    dishe = Dishes(user_id=user.id, query=call_data['query'], dishe_id=call_data['id'], get_by_id=True, callback_data=call_data)
    await dishe.send_post_by_id(call)
    dishe.print_all_time('Edit favourite')
    await call.answer(answer_text)
