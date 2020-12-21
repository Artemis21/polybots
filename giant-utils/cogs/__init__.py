"""Load the cogs."""
from cogs.meta import Meta
from cogs.rules import Rules
from cogs.utils import Utils

import discord


COGS = [Utils, Rules, Meta]


def setup(bot: discord.Client):
    """Load the cogs."""
    for cog in COGS:
        bot.add_cog(cog(bot))
