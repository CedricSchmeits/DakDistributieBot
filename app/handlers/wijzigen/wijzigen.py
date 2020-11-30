from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from app.middlewares.throttling import rate_limit
from app.misc import dp, bot

from app.models import User


@dp.message_handler(commands=["wijzigen"])
async def AdminWijzigenHandler(msg: types.Message):
    user = await User.get(msg.from_user.id)
    if user is None:
        await msg.answer("Deze gebruiker is onbekend en mag geen wijzigingen in het systeem doorvoeren.")

    keyboard = types.InlineKeyboardMarkup()
    if 'group' in msg.chat.type:
        isAdmin = False
        for chatMember in await bot.get_chat_administrators(msg.chat.id):
            if chatMember.user.id == msg.from_user.id:
                keyboard.insert(types.InlineKeyboardButton(text='Plaats', callback_data='wijzigingen_plaats'))
                break

    if user.is_superuser:
        keyboard.insert(types.InlineKeyboardButton(text='Editie', callback_data='wijzigingen_editie'))

    await msg.answer(f'In wel onderdeel wil je wijzigingen doorvoeren?', reply_markup=keyboard, disable_notification=True)
    await msg.delete()
