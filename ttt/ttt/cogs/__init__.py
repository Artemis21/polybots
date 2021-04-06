"""Load the cogs."""
from discord.ext import commands

from .games import Games
from .meta import Meta
from .players import Players
from .tags import Tags


COGS = [Meta, Players, Games, Tags]


def setup(bot: commands.Bot):
    """Load the cogs."""
    for cog in COGS:
        cog = cog(bot)
        bot.add_cog(cog)