"""Lists of objects."""
from discord.ext import commands

from tools import units


class Lists(commands.Cog):
    """Object lists cog."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot

    @commands.command(brief='Lists of units.', aliases=['us'])
    async def units(self, ctx: commands.Context):
        """Show a list of units.

        Examples:
        `{{pre}}units`
        `{{pre}}us`
        """
        await ctx.send(units.list_all())
