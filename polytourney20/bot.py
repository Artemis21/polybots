"""The main bot."""
import json
import logging

import discord
from discord.ext import commands

# must import models first to prevent circular import
import models

from tools.config import Config
from tools.helpcmd import Help


logging.basicConfig(level=logging.INFO)

config = Config()


def get_prefix(bot: commands.Bot, message: discord.Message) -> str:
    """Return the prefix (so that it updates)."""
    return config.prefix


bot = commands.Bot(command_prefix=get_prefix)
bot.load_extension('cogs')
bot.help_command = Help()

models.setup(bot)

with open('config.json') as f:
    token = json.load(f)['token']

bot.run(token)


