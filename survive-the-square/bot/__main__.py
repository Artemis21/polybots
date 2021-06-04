"""The main bot."""
import logging

from discord.ext import commands

from .main import config, ctx_logs, helpcmd


logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix=config.PREFIX, help_command=helpcmd.Help())
ctx_logs.setup(bot)
bot.load_extension('bot.cogs')

bot.run(config.TOKEN)
