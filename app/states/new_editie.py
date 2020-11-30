from aiogram.dispatcher.filters.state import StatesGroup, State

class NewEditie(StatesGroup):
    Naam = State()
    Url = State()
    Cover = State()
    Bevestigen = State()
