"""The main bot."""
import json
import logging

import discord
from discord.ext import commands

from tools.helpcmd import Help


logging.basicConfig(level=logging.INFO)

with open('config.json') as f:
    config = json.load(f)


bot = commands.Bot(command_prefix=config['prefix'])
bot.load_extension('cogs')
bot.help_command = Help()

bot.run(config['token'])
