"""The main bot."""
import logging

from .bot import bot
from .main import config


LOGS = (
    ('peewee', config.DB_LOG_LEVEL),
    ('discord.client', config.BOT_LOG_LEVEL)
)
for log, level in LOGS:
    logger = logging.getLogger(log)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '{levelname}:{name}:{message}', style='{'
    ))
    logger.addHandler(handler)
    logger.setLevel(level)


bot.run(config.BOT_TOKEN)
