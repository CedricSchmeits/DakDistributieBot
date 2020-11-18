from typing import List

from loguru import logger

from app.utils import Broadcast


async def notify_admins(admins: List[int]):
    count = await (Broadcast(admins, 'The bot is running!')).start()
    logger.info(f"{count} admins received messages")
