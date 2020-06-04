"""Utility commands cog."""
from discord.ext import commands
import discord

import typing

from tools import nameedit, massrole


Ctx = commands.Context


class Utils(commands.Cog):
    """Utility commands."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot

    @commands.command(brief='Rename a game channel.')
    async def rename(self, ctx: Ctx, *, name: str):
        """Rename a game channel.

        The new name must be a valid game name.
        Example: `{{pre}}rename The Square of Destruction`
        """
        await ctx.send(await nameedit.rename(ctx.channel, name))

    @commands.command(
        brief='Award a role to many people.', name='mass-role'
    )
    @commands.has_permissions(manage_roles=True)
    async def mass_role(self, ctx: Ctx, role: discord.Role,
                        *users: discord.Member):
        """Award a role to multiple people.

        Example: `{{pre}}mass-role @Division C @member1 @member2 @member3`
        """
        async with ctx.typing():
            await massrole.massrole(role, users)
        await ctx.send('Done :thumbsup:')

    @commands.command(brief='How many members a role has.')
    async def members(self, ctx, *, role: discord.Role):
        """Check how many people have a role.

        Example: `{{pre}}members @some-role`.
        """
        await ctx.send(f'{len(role.members)} people have that role.')
