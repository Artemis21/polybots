
"""Load the cogs."""
import discord

from .leaderboard import Leaderboard
from .meta import Meta


COGS = [Leaderboard, Meta]


def setup(bot: discord.Client):
    """Load the cogs and perform other setup tasks."""
    for cog in COGS:
        cog = cog(bot)
        bot.add_cog(cog)
