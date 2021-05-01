"""Tools for creating and viewing logs."""
import datetime
import io
import logging
from typing import Optional

import discord

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


def get_logs(
        start: Optional[datetime.datetime] = None,
        level: int = logging.INFO,
        max_logs: Optional[int] = 1000) -> discord.File:
    """Get a Discord attachment for a list of logs."""
    logs = Log.get_logs(start, level, max_logs)
    stream = io.StringIO()
    for log in logs:
        level = logging.getLevelName(log.level)
        date = log.created_at.strftime('%H:%M:%S %d/%m/%y')
        stream.write(f'{date} [{level}] {log.content}')
    stream.seek(0)
    return discord.File(stream, 'ttt_logs.txt')
