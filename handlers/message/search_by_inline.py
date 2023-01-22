
from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from app import dp
from functions.main import Dishes, get_parameters

@dp.message_handler(filters.Text(contains=['get_id=']), state='*')
async def search_by_inline(message: types.Message, state: FSMContext):
    user = message.from_user
    parameters = get_parameters(message.text)

    dishe_id = int(parameters.get('get_id'))
    query = parameters.get('query_text', '')

    dishe = Dishes(user_id=user.id, query=query,dishe_id=int(dishe_id), get_by_id=True)
    await dishe.send_post_by_id(message)
    dishe.print_all_time('Get id')
