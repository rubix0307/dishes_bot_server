from aiogram import types
from app import dp
from functions.main import Dishes
from functions.markups import set_photo_call_menu, get_call_data


@dp.callback_query_handler(set_photo_call_menu.filter(), state='*')
async def show_dish(call: types.CallbackQuery, callback_data: dict()):

    user = call.from_user
    call_data = get_call_data(callback_data)

    dishe = Dishes(user_id=user.id, query=call_data['query'], dishe_id=call_data['id'], get_by_id=True, callback_data=call_data)
    await dishe.send_post_by_id(call)
    dishe.print_all_time('Edit photo')
