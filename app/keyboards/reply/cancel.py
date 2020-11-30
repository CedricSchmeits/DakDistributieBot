from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_markup.insert(KeyboardButton(text='Annuleren'))
