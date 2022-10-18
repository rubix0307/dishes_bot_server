import time
from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

from app import bot, dp
from functions import Article, edit_preview, get_call_data, get_data_dish
from markups import set_photo_call_menu


@dp.callback_query_handler(set_photo_call_menu.filter())
async def edit_photo(call: types.CallbackQuery, callback_data: dict()):
    start = time.time()
    user = call.from_user
    call_data = get_call_data(callback_data)

    data = get_data_dish(call_data['id'])
    article = Article(data, callback_data=call_data, user_id=user.id)

    article, call_data = edit_preview(article, call_data)


    message_data = {
        'parse_mode': 'html',
        'reply_markup': article.get_markup(),
        'text': article.get_message_text(),
        
    }
    get_time = time.time()
    
    try:

        try:
            await bot.edit_message_text(
                inline_message_id=call.inline_message_id,
                **message_data,
            )

        except:
            await bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                **message_data,
            )

    except MessageNotModified:
        await call.answer('Выбрано текущее фото')

    finally:
        await call.answer()
        print(f'| photo  | get in {round(get_time - start, 3)}s')
        print(f'| photo  | all in {round(time.time() - start, 3)}s', end='\n'*2)
