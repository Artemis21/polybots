"""The main bot."""
import json
import logging

from discord.ext import commands

from cogs import meta, lookups, lists
from tools import helpcmd


logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix='p?', help_command=helpcmd.Help())

for cog in (meta.Meta, lookups.Lookups, lists.Lists):
    bot.add_cog(cog(bot))

with open('secrets.json') as f:
    token = json.load(f)['token']

bot.run(token)
