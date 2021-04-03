"""The main bot."""
import logging

from discord.ext import commands

from .main import config, helpcmd


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


bot = commands.Bot(
    command_prefix=config.BOT_PREFIX, help_command=helpcmd.Help()
)
bot.load_extension('ttt.cogs')

bot.run(config.BOT_TOKEN)
