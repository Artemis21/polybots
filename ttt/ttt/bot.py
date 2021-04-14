"""Set up the bot."""
from discord.ext import commands

from .main import config, helpcmd


bot = commands.Bot(
    command_prefix=config.BOT_PREFIX,
    help_command=helpcmd.Help()
)

bot.load_extension('ttt.cogs')
