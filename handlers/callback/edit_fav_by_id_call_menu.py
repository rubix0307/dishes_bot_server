from aiogram import types
from app import bot, dp
from db.functions import sql
from functions import Article, edit_preview, get_call_data, get_data_dish
from markups import edit_fav_by_id_call_menu


@dp.callback_query_handler(edit_fav_by_id_call_menu.filter())
async def show_dish(call: types.CallbackQuery, callback_data: dict()):

    user = call.from_user
    call_data = get_call_data(callback_data)

    if not call_data['fav']:
        answer_text = 'Добавлено в избранное'
        sql(
            f'''INSERT INTO fav_dish_user (user_id, dish_id) VALUES ({user.id},{call_data['id']})''',
            commit=True,
        )
    else:
        answer_text = 'Убрано из избранного'
        sql(
            f'''DELETE FROM fav_dish_user WHERE fav_dish_user.user_id = {user.id} AND fav_dish_user.dish_id = {call_data['id']}''',
            commit=True,
        )

    call_data['fav'] = int(not call_data['fav'])

    data_list_item = get_data_dish(call_data['id'])

    article = Article(data_list_item, callback_data=call_data, user_id=user.id)
    article, call_data = edit_preview(article, call_data)


    message_data = {
        'text': article.get_message_text(),
        'reply_markup': article.get_markup(),
        'parse_mode': 'html',
    }

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

    finally:
        await call.answer(answer_text)
