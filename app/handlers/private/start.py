from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from app.middlewares.throttling import rate_limit
from app.misc import dp


@rate_limit(30, 'command_start')
@dp.message_handler(CommandStart())
async def command_start_handler(msg: types.Message):
    await msg.answer(f'Hello, {msg.from_user.full_name}!')
