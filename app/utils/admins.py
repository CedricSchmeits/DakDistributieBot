from typing import List, Union
from asyncpg.exceptions import UndefinedTableError
from loguru import logger

from app.models.user import User
from app.utils import Broadcast


async def NotifyAdmins(admins: List[int]):
    count = await (Broadcast(admins, 'The bot is running!')).start()
    logger.info(f"{count} admins received messages")


async def CheckAdmins(admins: List[int]):
    for userId in admins:
        try:
            user = await User.query.where(User.id == userId).gino.first()
            if user:
                if not user.is_superuser:
                    await user.update(is_superuser=True).apply()
            else:
                logger.error(f"SuperUser {userId} is not registered in bot")
        except UndefinedTableError:
            logger.error("Could not retrieve superuser")

async def CreateSuperUser(userId: int, enabled: bool) -> bool:
    user = await User.query.where(User.id == userId).gino.first()
    if not user:
        logger.error("User is not registered in bot")
        raise ValueError("User is not registered in bot")

    logger.info(
        "Loaded user {user}. It's registered at {register_date}.",
        user=user.id,
        register_date=user.created_at,
    )
    await user.update(is_superuser=enabled).apply()
    logger.warning("User {user} now IS{enabled} superuser", user=userId, enabled="" if enabled else " NOT")

    return True
