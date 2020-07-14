"""Object lookups."""
from discord.ext import commands

from tools import units


class Lookups(commands.Cog):
    """Object lookups cog."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot

    @commands.command(brief='Lookup a unit.', aliases=['u'])
    def unit(self, ctx: commands.Context, *, search: units.lookup):
        """Search for a unit to show stats.

        Examples:
        `{{pre}}unit warrior`
        `{{pre}}u wa`
        `{{pre}}unit fire dragon`
        `{{pre}}u dr`
        """
        await ctx.send(embed=units.embed(search))
