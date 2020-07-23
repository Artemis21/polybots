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

    @commands.command(brief='Lookup a task.', aliases=['tk'])
    async def task(self, ctx: Ctx, *, task: ObjectConverter('task')):
        """Search for a task to show details.

        Examples:
        `{{pre}}task killer`
        `{{pre}}tk ki`
        `{{pre}}task pacifist`
        `{{pre}}tk pa`
        """
        await ctx.send(embed=task)

    @commands.command(brief='Lookup a tech.', aliases=['technology', 't'])
    async def tech(self, ctx: Ctx, *, tech: ObjectConverter('tech')):
        """Search for a technology to show details.

        Examples:
        `{{pre}}tech mathematics`
        `{{pre}}t ma`
        `{{pre}}tech aquatism`
        `{{pre}}t aq`
        """
        await ctx.send(embed=tech)
