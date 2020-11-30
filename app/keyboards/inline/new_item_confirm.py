from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

newItemConfirm = InlineKeyboardMarkup()
newItemConfirm.insert(InlineKeyboardButton(
    text='Ja, dat klopt', callback_data='confirm_item'
))
newItemConfirm.insert(InlineKeyboardButton(
    text='Nee, reset', callback_data='reset_item'
))
