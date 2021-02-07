
"""Load the cogs."""
import discord

from .games import Games
from .meta import Meta
from .players import Players


COGS = [Players, Games, Meta]


def setup(bot: discord.Client):
    """Load the cogs and perform other setup tasks."""
    for cog in COGS:
        cog = cog(bot)
        bot.add_cog(cog)
