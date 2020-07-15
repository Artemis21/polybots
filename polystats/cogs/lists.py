"""Lists of objects."""
from discord.ext import commands

from tools.objects import list_all


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
        await ctx.send(list_all('unit'))

    @commands.command(brief='Lists of skills.', aliases=['ss'])
    async def skills(self, ctx: commands.Context):
        """Show a list of skills.

        Examples:
        `{{pre}}skills`
        `{{pre}}ss`
        """
        await ctx.send(list_all('skill'))

    @commands.command(brief='Lists of tasks.', aliases=['ts'])
    async def tasks(self, ctx: commands.Context):
        """Show a list of tasks.

        Examples:
        `{{pre}}tasks`
        `{{pre}}ts`
        """
        await ctx.send(list_all('task'))

    