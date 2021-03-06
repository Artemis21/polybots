"""Load the cogs."""
from cogs.meta import Meta
from cogs.players import Players
from cogs.games import Games
from cogs.other import Other
from cogs.tags import Tags

from tools import datautils

import discord


COGS = [Meta, Players, Games, Tags, Other]


def setup(bot: discord.Client):
    """Load the cogs and perform other setup tasks."""
    for cog_class in COGS:
        cog = cog_class(bot)
        bot.add_cog(cog)
    datautils.client = bot
