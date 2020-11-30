from aiogram import types
from loguru import logger


async def setup_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "start"),
            types.BotCommand("wijzigen", "Toevoegen van edities, plaatsen, wijken en/of straten."),
            #types.BotCommand("nieuwe_editite", "Registreren van een nieuwe editie"),
            types.BotCommand("claimen", "Claimen van een straat, zodat anderen weten dat je ermee bezig bent."),
            types.BotCommand("gedaan", "Melden van een straat dat deze gedaan is."),
        ]
    )
    logger.info('Standard commands are successfully configured')
