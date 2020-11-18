from dataclasses import dataclass

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


@dataclass
class IsReplyFilter(BoundFilter):
    """
    EXAMPLE
    Filtered message should be reply to another message
    """

    key = "is_reply"
    is_reply: bool

    async def check(self, message: types.Message) -> bool:
        return self.is_reply == message.reply_to_message
