from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp
from handlers.admin.functions import *
from markups import mails_call_filter





@dp.message_handler(state='*', commands=['cancel'])
async def mailing_cancel_handler(message: types.Message, state=FSMContext):
    await mailing_cancel(message=message, state=state)


@dp.message_handler(state='*', commands=['mails'])
@dp.callback_query_handler(lambda call: mails_call_filter['edit_text'] in call.data, state='*')
async def mailing_start_handler(message: types.Message, state: FSMContext):
    await mailing_start(message=message, state=state)


@dp.message_handler(state=Form.text)
async def mailing_set_text_handler(message: types.Message, state: FSMContext):
    await mailing_set_text(message=message, state=state)

@dp.callback_query_handler(lambda call: mails_call_filter['preview_state'] in call.data, state='*')
async def mailing_start_handler(message: types.Message, state: FSMContext):
    await edit_preview_state(message=message, state=state)

@dp.callback_query_handler(lambda call: mails_call_filter['paddings_state'] in call.data, state='*')
async def mailing_start_handler(message: types.Message, state: FSMContext):
    await edit_paddings_state(message=message, state=state)

@dp.callback_query_handler(lambda call: mails_call_filter['self_send'] in call.data, state='*')
async def mailing_start_handler(message: types.Message, state: FSMContext):
    await send_mailing(message, state, only_me=True)

@dp.callback_query_handler(lambda call: mails_call_filter['send_all'] in call.data, state='*')
async def mailing_start_handler(message: types.Message, state: FSMContext):
    await send_mailing(message, state, only_me=False)

@dp.callback_query_handler(lambda call: mails_call_filter['settings'] in call.data, state='*')
async def mailing_start_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await get_preview_mail(message=message, data=data)
    await Form.next()
    



























