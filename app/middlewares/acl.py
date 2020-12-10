from typing import Optional
from loguru import logger

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from app.models import User


class ACLMiddleware(BaseMiddleware):
    @staticmethod
    async def setup_chat(data: dict, user: types.User, chat: Optional[types.Chat] = None):
        userId = user.id
        chatId = chat.id if chat else user.id
        chatType = chat.type if chat else "private"

        user = await User.get(userId)
        if user is None:
            user = await User.create(id=userId)
            logger.info(f"new user: {userId}")


        data["user"] = user

    async def on_pre_process_message(self, message: types.Message, data: dict):
        logger.info(f"on_pre_process_message: {message}; {data}")
        await self.setup_chat(data, message.from_user, message.chat)

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: dict):
        logger.info(f"on_pre_process_message: {query}; {data}")
        await self.setup_chat(data, query.from_user, query.message.chat if query.message else None)
