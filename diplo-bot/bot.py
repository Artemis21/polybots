"""The main bot."""
import logging

from discord.ext import commands

from main import config, helpcmd


logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix=config.PREFIX, help_command=helpcmd.Help())
bot.load_extension('cogs')

bot.run(config.TOKEN)
