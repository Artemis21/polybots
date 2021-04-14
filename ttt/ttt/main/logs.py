"""Tools for creating and viewing logs."""
import logging

from .config import BOT_LOG_CHANNEL_ID, TT_LOG_LEVEL
from .. import bot
from ..models.logs import Log


async def log(message: str, level: int = logging.INFO):
    """Log a message to the database and log channel."""
    Log.create(content=message, level=level)
    if level < TT_LOG_LEVEL:
        return
    channel = bot.bot.get_channel(BOT_LOG_CHANNEL_ID)
    if not channel:
        return
    level_name = logging.getLevelName(level)
    await channel.send(f'**{level_name}:** {message}')
