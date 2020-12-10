from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.markdown import hbold, hide_link
from loguru import logger

from app.keyboards.reply import cancel_markup
from app.misc import dp
from app.states.new_editie import NewEditie
from app.models.editie import Editie
from app.keyboards.inline import newItemConfirm
from app.utils.misc.validate_link import ValidatePhotoLink
from app.middlewares.throttling import rate_limit

##########################################################
# Nieuwe Editie
##########################################################
@dp.message_handler(Text(equals='annuleren', ignore_case=True), state=NewEditie)
async def AdminEditieCancel(message: types.Message, state: FSMContext):
    await message.answer("De registratie van een nieuwe editie is geannuleerd",
                         reply_markup=ReplyKeyboardRemove())
    await state.finish()

@rate_limit(30)
@dp.message_handler(Command('nieuwe_editie'), is_superuser=True)
async def AdminEditieAdd(message: types.Message):
    logger.info("nieuwe editie registreren")
    await message.answer(f'U begint met de registratie van een nieuwe editie.\nVoer de naam van de editie in:',
                         reply_markup=cancel_markup)
    await NewEditie.first()


@dp.message_handler(state=NewEditie.Naam, is_superuser=True)
async def AdminEditieSetName(message: types.Message, state: FSMContext):
    if len(message.text) < 2:
        return await message.answer(f'De naam mag niet korter zijn dan 2 karakters. Probeer het opnieuw.')
    elif len(message.text) > 1024:
        return await message.answer(f'De naam mag niet langer zijn dan 1000 tekens. Probeer het opnieuw.')

    naam = message.text
    item = {"naam": naam}
    await message.answer(f'Editie "{naam}"\nVoer nu de URL in:')
    await NewEditie.next()
    await state.update_data(item=item)


@dp.message_handler(state=NewEditie.Url, is_superuser=True)
async def AdminEditieSetUrl(message: types.Message, state: FSMContext):
    if not message.text:
        return await message.answer('URL mag niet leeg zijn, probeer opnieuw.')
    elif len(message.text) > 128:
        return await message.answer('De URL kan niet langer zijn dan 128 karakters, probeer opnieuw')

    data = await state.get_data()
    item = data.get('item')
    item["url"] = message.text
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.insert(types.KeyboardButton(
        text='Annuleren'
    ))
    mk.insert(types.KeyboardButton(
        text='Geen'
    ))
    await message.answer(
        f'Geef nu een link naar de cover door:',
        reply_markup=mk,
    )
    await NewEditie.next()
    await state.update_data(item=item)


@dp.message_handler(state=NewEditie.Cover, is_superuser=True)
async def AdminEditieSetCover(message: types.Message, state: FSMContext):
    if not message.text:
        return await message.answer('Cover mag niet leeg zijn, probeer opnieuw.')
    elif len(message.text) > 128:
        return await message.answer('De Cover kan niet langer zijn dan 128 karakters, probeer opnieuw')
    elif not ValidatePhotoLink(message.text):
        return await message.answer(f'De cover link is geen valide foto link: {message.text}')

    data = await state.get_data()
    item = data.get('item')
    cover = message.text
    item["cover"] = cover

    answer = "\n\n".join((f'{hide_link(item["cover"])} {hbold("Editie:")}\n{item["naam"]}',
                          f'{hbold("URL:")}\n{item["url"]}'))
    await message.answer(answer, reply_markup=newItemConfirm)
    await NewEditie.next()
    await state.update_data(item=item)


@dp.callback_query_handler(is_superuser=True, state=NewEditie.Confirm, text='confirm_item')
async def AdminEditieConfirm(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item = data.get('item')
    new_item = await Editie.create(**item)
    logger.info(f'The subject "{new_item}" was successfully added')
    await query.message.answer(f"Nieuwe editie {item['naam']} is toegevoegd", reply_markup=ReplyKeyboardRemove())
    await state.finish()
    await query.answer()


@dp.callback_query_handler(is_superuser=True, state=NewEditie.Confirm, text='reset_item')
async def AdminEditieReset(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("De registratie van een nieuwe editie is geannuleerd",
                               reply_markup=ReplyKeyboardRemove())
    await state.finish()
    await query.answer()

@dp.callback_query_handler(is_superuser=True, text='wijzigingen_editie')
async def AdminWijzigenEditie(query: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.insert(types.InlineKeyboardButton(text='Nieuwe Toevoegen', callback_data='nieuwe_editie'))
    keyboard.insert(types.InlineKeyboardButton(text='Activeren', callback_data='activeer_editie'))
    await query.message.answer(f"Wat wil je aan de edities veranderen?",
                               reply_markup=keyboard, disable_notification=True)
    await query.message.delete()



logger.info("wijzigen_panel successfully configured")
