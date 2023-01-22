
from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp
from functions.admin import *
from functions.main import Dishes, check_activity, dont_get_you
from functions.markups import get_back_to_inline, get_home_button, mails_call_filter






@dp.message_handler(state='*')
async def search_by_message(message: types.Message):
    user = message.from_user
    check_result = await check_activity(message)

    if check_result:
        text = message.text
        

        if text.isdigit():
            dishe = Dishes(user_id=user.id, dishe_id=int(text), get_by_id=True)
            if dishe.dishes_data_list:
                await dishe.send_post_by_id(message)
            else:
                await dont_get_you(message)

        else:
            dishe = Dishes(user_id=user.id, query=text, get_by_query=True)
            if dishe.dishes_data_list:
                data_list_len = len(dishe.dishes_data_list)
                answer = await message.answer(
                    text=f'''{'Огромное количество' if data_list_len >= 50 else data_list_len} вариантов того что искали''',
                    reply_markup=InlineKeyboardMarkup().add(get_back_to_inline('Результат', query_text=text)),
                )
                await message.delete()
                await update_last_message(message, castom_message_id=answer.message_id)
            else:
                await dont_get_you(message)
        





