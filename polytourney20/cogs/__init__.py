"""Load the cogs."""
from cogs.meta import Meta
from cogs.players import Players
from cogs.games import Games
from cogs.tags import Tag

from tools import datautils

import discord


COGS = [Players, Games, Tag, Meta]


def setup(bot: discord.Client):
    """Load the cogs and perform other setup tasks."""
    for cog_class in COGS:
        cog = cog_class(bot)
        bot.add_cog(cog)
    datautils.client = bot
