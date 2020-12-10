import typing

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.markdown import hbold, hide_link
from aiogram.dispatcher.filters.state import StatesGroup, State

from loguru import logger

from app import utils, config
from app.middlewares.throttling import rate_limit
from app.misc import dp, db, bot
from app.keyboards.reply import cancel_markup
from app.keyboards.inline import newItemConfirm, NameIdKeyboard
from app.models import Groep

class GroupKeyboard(NameIdKeyboard):
    callbackName = 'group'


from app import utils, config

async def NotifyAdminsNewGroup(chat):
    count = await (utils.Broadcast(config.SUPERUSER_ID,
                                   "Ik ben net toegevoegd bij een nieuwe groep.\n"\
                                   f"Groep naam: {chat.title}\n"\
                                   f"Groep id:   {chat.id}\n"\
                                   f"\nWil je deze toevoegen?")).start()


@dp.message_handler(content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def AdminGroupNewChatMember(message: types.Message):
    for member in message.new_chat_members:
        if member.id == config.BOT_ID:
            await NotifyAdminsNewGroup(message.chat)
            await message.answer("Hallo ik ben de distributie bot,\n"\
                                 "Voordat ik volledig operationeel wordt dient een van de "\
                                 "superadmins deze groep te accepteren. Daarna kan ik de "\
                                 "administratie van de distributie uit jullie handen nemen "\
                                 "met de volgende commando's:\n/claimen\n/gedaan\n"\
                                 "De admins van deze groep hebben tevens de mogelijkheid "\
                                 "om via het commando /wijzigen, wijzigingen door te brengen "\
                                 "in de gebruikte plaatsen, wijken en straten in deze groep.")
        else:
            await message.answer(f"Welkom {member.title} in de {message.chat.title} groep.\n"\
                                 f"Ik ben de distributie bot van deze groep, bij mij kun je "\
                                 f"opvragen welke straten/wijken in jou groep nog vrij zijn "\
                                 f"om te distributeren. Tevens kun je ook straten claimen en "\
                                 f"uiteindelijk als ze gedaan zijn ook als gedaan afmelden.\n\n"\
                                 f"De commando's die ik accepteer, zijn onder andere:\n"\
                                 f"/claimen\n/gedaan\n")

##########################################################
# Groep Menu
##########################################################
@dp.callback_query_handler(is_superuser=True, text='wijzigingen_groep')
async def AdminChangesGroup(query: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.insert(types.InlineKeyboardButton(text='Nieuwe Toevoegen', callback_data='group_new'))
    keyboard.insert(types.InlineKeyboardButton(text='Wijzigen', callback_data='group_change'))
    keyboard.insert(types.InlineKeyboardButton(text='Verwijderen', callback_data='group_delete'))
    await query.message.answer(f"Wat wil je aan de edities veranderen?",
                               reply_markup=keyboard, disable_notification=True)
    await query.message.delete()


##########################################################
# Nieuwe Groep
##########################################################
class NewGroupStates(StatesGroup):
    GroupId = State()
    Confirm = State()

@dp.message_handler(Text(equals='annuleren', ignore_case=True), state=NewGroupStates)
async def AdminGroupCancel(message: types.Message, state: FSMContext):
    await message.answer("De registratie van een nieuwe groep is geannuleerd",
                         reply_markup=ReplyKeyboardRemove(), disable_notification=True)
    await message.delete()
    await state.finish()

@rate_limit(30)
@dp.callback_query_handler(text='group_new', is_superuser=True)
async def AdminGroupAdd(query: types.CallbackQuery, state: FSMContext):
    logger.info("nieuwe groep registreren")
    await query.message.answer(f'U begint met de registratie van een nieuwe groep.\nVoer het id van de groep in:',
                               reply_markup=cancel_markup, disable_notification=True)
    await query.message.delete()
    await NewGroupStates.first()

@dp.message_handler(state=NewGroupStates.GroupId, is_superuser=True)
async def AdminGroupSetId(message: types.Message, state: FSMContext):
    groupId = int(message.text)
    if groupId >= 0:
        await message.delete()
        return await message.answer('Groep Id moet kleiner zijn dan 0.', disable_notification=True)

    chat = await bot.get_chat(groupId)

    group = await Groep.query.where(Groep.chatId == groupId).gino.first()
    logger.info(f"groepId: {groupId}; groep: {group}")
    if group is not None:
        await message.delete()
        return await message.answer(f'Groep {chat.title} ({groupId}) is al geregistreerd.', disable_notification=True)

    item = {"chatId": groupId}
    item["naam"] = chat.title


    answer = f'{hbold("Groep id:")} {item["chatId"]}\n'\
             f'{hbold("Naam:")} {item["naam"]}'
    await message.answer(answer, reply_markup=newItemConfirm, disable_notification=True)
    await message.delete()
    await NewGroupStates.next()
    await state.update_data(item=item)


@dp.callback_query_handler(is_superuser=True, state=NewGroupStates.Confirm, text='confirm_item')
async def AdminGroupConfirm(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item = data.get('item')
    new_item = await Groep.create(chatId=item['chatId'])
    logger.info(f'The subject "{new_item}" was successfully added')
    await query.message.answer(f"Nieuwe groep {item['naam']} is toegevoegd",
                               reply_markup=ReplyKeyboardRemove(), disable_notification=True)
    await state.finish()
    await query.answer()
    await query.message.delete()


@dp.callback_query_handler(is_superuser=True, state=NewGroupStates.Confirm, text='reset_item')
async def AdminGroupReset(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("De registratie van een nieuwe groep is geannuleerd",
                               reply_markup=ReplyKeyboardRemove(), disable_notification=True)
    await state.finish()
    await query.answer()
    await query.delete()
    await query.message.delete()

##########################################################
# Delete Group
##########################################################
class GroupDeleteStates(StatesGroup):
    GroupId = State()
    Confirm = State()

#@dp.message_handler(Text(equals='annuleren', ignore_case=True), state=GroupDeleteStates)
#async def AdminGroepVerwijderCancel(message: types.Message, state: FSMContext):
#    await message.answer("De verwijdering van een groep is geannuleerd",
#                         reply_markup=ReplyKeyboardRemove(), disable_notification=True)
#    await message.delete()
#    await state.finish()

@dp.callback_query_handler(GroupKeyboard.filter(action='cancel'),
                           state=GroupDeleteStates,
                           is_superuser=True)
async def AdminGroupDeleteCancel(query: types.CallbackQuery, callback_data: typing.Dict[str, str], state: FSMContext):
    logger.info(f"AdminGroupDeleteCancel: query: {query}; callback_data: {callback_data}")
    await query.message.answer("De verwijdering van een groep is geannuleerd",
                         reply_markup=ReplyKeyboardRemove(), disable_notification=True)
    await query.message.delete()
    await state.finish()

@rate_limit(30)
@dp.callback_query_handler(text='group_delete', is_superuser=True)
async def AdminGroupDeleteStart(query: types.CallbackQuery, state: FSMContext):
    logger.info("groep verwijderen")
    keyboard = GroupKeyboard()
    for group in await db.all(Groep.query):
        chat = await bot.get_chat(group.chatId)
        keyboard.Append(chat.title, group.id, 'delete')

    await query.message.answer(f'Kies een groep uit die U wilt verwijderen.',
                               reply_markup=keyboard.Generate(), disable_notification=True)
    await query.message.delete()
    await GroupDeleteStates.first()

@dp.message_handler(is_superuser=True, state=GroupDeleteStates)
async def AdminGroupTestCancel(message: types.Message, state: FSMContext):
    logger.info(f"message received: {message.text} - {state}")
    await state.finish()


@dp.callback_query_handler(GroupKeyboard.filter(action='delete'),
                           state=GroupDeleteStates.GroupId,
                           is_superuser=True)
async def AdminGroupVerwijderenId(query: types.CallbackQuery, callback_data: typing.Dict[str, str], state: FSMContext):
    groupId = int(callback_data['id'])
    if groupId < 0:
        return await message.answer('Ongeldige groep id.', disable_notification=True)

    item = {"id": groupId}
    groep = await Groep.get(groupId)
    item["chatId"] = groep.chatId
    chat = await bot.get_chat(groep.chatId)
    item["naam"] = chat.title

    answer = f'{hbold("Groep id:")} {item["chatId"]}\n'\
             f'{hbold("Naam:")} {item["naam"]}'
    await query.message.answer(answer, reply_markup=newItemConfirm, disable_notification=True)
    await query.message.delete()
    await GroupDeleteStates.next()
    await state.update_data(item=item)

@dp.callback_query_handler(is_superuser=True, state=GroupDeleteStates.Confirm, text='confirm_item')
async def AdminGroupDeleteConfirm(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item = data.get('item')
    groep = await Groep.get(item['id'])
    await groep.delete()
    logger.info(f'The subject "{groep}" was successfully deleted')
    await query.message.answer(f"Groep {item['naam']} is verwijderd",
                               reply_markup=ReplyKeyboardRemove(), disable_notification=True)
    await state.finish()
    await query.answer()
    await query.message.delete()


@dp.callback_query_handler(is_superuser=True, state=GroupDeleteStates.Confirm, text='reset_item')
async def AdminGroupDeleteReset(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("De verwijdering van een nieuwe groep is geannuleerd",
                               reply_markup=ReplyKeyboardRemove(), disable_notification=True)
    await state.finish()
    await query.answer()
    await query.message.delete()

##########################################################
# Edit Group
##########################################################
class GroupChangeStates(StatesGroup):
    GroupId = State()
    NewChatId = State()
    Confirm = State()

@rate_limit(30)
@dp.callback_query_handler(text='group_change', is_superuser=True)
async def AdminGroupChangeStart(query: types.CallbackQuery, state: FSMContext):
    logger.info("groep veranderen")
    keyboard = GroupKeyboard()
    for group in await db.all(Groep.query):
        chat = await bot.get_chat(group.chatId)
        keyboard.Append(chat.title, group.id, 'change')

    await query.message.answer(f'Kies een groep uit die U wilt veranderen.',
                               reply_markup=keyboard.Generate(), disable_notification=True)
    await query.message.delete()
    await GroupChangeStates.first()

@dp.callback_query_handler(GroupKeyboard.filter(action='cancel'),
                           state=GroupChangeStates,
                           is_superuser=True)
async def AdminGroupChangeCancel(query: types.CallbackQuery, callback_data: typing.Dict[str, str], state: FSMContext):
    logger.info(f"AdminGroupChangeCancel")
    await query.message.answer("Het veranderen van een groep is geannuleerd",
                         reply_markup=ReplyKeyboardRemove(), disable_notification=True)
    await query.message.delete()
    await state.finish()

@dp.callback_query_handler(GroupKeyboard.filter(action='change'),
                           state=GroupChangeStates.GroupId,
                           is_superuser=True)
async def AdminGroupChangeGetGroupId(query: types.CallbackQuery, callback_data: typing.Dict[str, str], state: FSMContext):
    groupId = int(callback_data['id'])
    if groupId < 0:
        return await message.answer('Ongeldige groep id.', disable_notification=True)

    item = {"id": groupId}
    group = await Groep.get(groupId)
    item["chatId"] = group.chatId
    chat = await bot.get_chat(group.chatId)
    item["naam"] = chat.title

    answer = f'{hbold("Groep id:")} {item["chatId"]}\n'\
             f'{hbold("Naam:")} {item["naam"]}\n'\
             'Voer het nieuwe groep id in:'
    await query.message.answer(answer, reply_markup=cancel_markup, disable_notification=True)
    await query.message.delete()
    await GroupChangeStates.next()
    await state.update_data(item=item)

@dp.message_handler(state=GroupChangeStates.NewChatId, is_superuser=True)
async def AdminGroupChangeGetChatId(message: types.Message, state: FSMContext):
    try:
        chatId = int(message.text)
    except ValueError:
        if message.text == "Annuleren":
            await message.answer("Het veranderen van een groep is geannuleerd",
                                 reply_markup=ReplyKeyboardRemove(), disable_notification=True)
            await message.delete()
            await state.finish()
            return

    if chatId >= 0:
        await message.delete()
        return await message.answer('Groep Id moet kleiner zijn dan 0.', disable_notification=True)

    chat = await bot.get_chat(chatId)

    group = await Groep.query.where(Groep.chatId == chatId).gino.first()
    logger.info(f"groepId: {chatId}; groep: {group}")
    if group is not None:
        await message.delete()
        return await message.answer(f'Groep {chat.title} ({chatId}) is al geregistreerd.', disable_notification=True)

    data = await state.get_data()
    item = data.get('item')

    group = await Groep.query.where(Groep.chatId == int(item['id'])).gino.first()
    if group is not None:
        item["chatId"] = chatId
        item["naam"] = chat.title


    answer = 'Omzetten van de oude groep naar de nieuwe groep:\n'\
             f'{hbold("Groep id:")} {item["chatId"]}\n'\
             f'{hbold("Naam:")} {item["naam"]}'
    await message.answer(answer, reply_markup=newItemConfirm, disable_notification=True)
    await message.delete()
    await GroupChangeStates.next()
    await state.update_data(item=item)


@dp.callback_query_handler(is_superuser=True, state=GroupChangeStates.Confirm, text='confirm_item')
async def AdminGroupChangeConfirm(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item = data.get('item')
    group = await Groep.get(item['id'])
    await group.update(chatId=item['chatId']).apply();

    logger.info(f'The subject "{group}" was successfully deleted')
    await query.message.answer(f"Groep {item['naam']} is veranderd",
                               reply_markup=ReplyKeyboardRemove(), disable_notification=True)
    await state.finish()
    await query.answer()
    await query.message.delete()


@dp.callback_query_handler(is_superuser=True, state=GroupChangeStates.Confirm, text='reset_item')
async def AdminGroupChangeReset(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("De verandering van een groep is geannuleerd",
                               reply_markup=ReplyKeyboardRemove(), disable_notification=True)
    await state.finish()
    await query.answer()
    await query.message.delete()
