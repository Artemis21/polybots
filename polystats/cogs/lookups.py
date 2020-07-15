"""Object lookups."""
from discord.ext import commands

from tools.objects import embed, ObjectConverter


Ctx = commands.Context


class Lookups(commands.Cog):
    """Object lookups cog."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot

    @commands.command(brief='Lookup a unit.', aliases=['u'])
    async def unit(self, ctx: Ctx, *, unit: ObjectConverter('unit')):
        """Search for a unit to show stats.

        Examples:
        `{{pre}}unit warrior`
        `{{pre}}u wa`
        `{{pre}}unit fire dragon`
        `{{pre}}u dr`
        """
        await ctx.send(embed=unit)

    @commands.command(brief='Lookup a skill.', aliases=['s'])
    async def skill(self, ctx: Ctx, *, skill: ObjectConverter('skill')):
        """Search for a skill to show information.

        Examples:
        `{{pre}}skill freeze area`
        `{{pre}}s fa`
        `{{pre}}skill dash`
        `{{pre}}s da`
        """
        await ctx.send(embed=skill)
