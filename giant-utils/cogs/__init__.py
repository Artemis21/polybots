"""Load the cogs."""
from cogs.meta import Meta
from cogs.utils import Utils

import discord


COGS = [Utils, Meta]


def setup(bot: discord.Client):
    """Load the cogs."""
    for cog_class in COGS:
        cog = cog_class(bot)
        bot.add_cog(cog)
