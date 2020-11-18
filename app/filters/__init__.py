from loguru import logger

from app.misc import dp

from .is_reply import IsReplyFilter

if __name__ == "app.filters":
    text_messages = [
        dp.message_handlers,
        dp.edited_message_handlers,
        dp.channel_post_handlers,
        dp.edited_channel_post_handlers,
    ]

    dp.filters_factory.bind(IsReplyFilter, event_handlers=text_messages)

    logger.info('Filters are successfully configured')
