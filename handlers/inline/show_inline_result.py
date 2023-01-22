from aiogram import types
from aiogram.dispatcher import filters

from app import dp
from functions.main import send_inline_result
from functions.markups import filters as inline_filters


@dp.inline_handler(filters.Text(contains=[inline_filters['favorites']]), state='*')
async def main(query: types.InlineQuery):
    await send_inline_result(query, get_by_favorites=True)

@dp.inline_handler(filters.Text(contains=[inline_filters['category']]), state='*')
async def main(query: types.InlineQuery):
    await send_inline_result(query, get_by_category=True)

@dp.inline_handler()
async def main(query: types.InlineQuery):
    await send_inline_result(query, get_by_query=True)









