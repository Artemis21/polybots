"""Utility commands cog."""
from discord.ext import commands
import discord

import typing

from tools import nameedit, roles


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

    @commands.has_permissions(manage_channels=True)
    @commands.command(brief='Reset a division category.')
    async def reset(self, ctx: Ctx):
        """Reset a division category.

        This will delete every channel in this category, and add channels
        named #time-out-glitches-and-breaks, #general, #game-1, #game-2...
        #game-8.

        Example: `{{pre}}reset`
        """
        async with ctx.typing():
            error = await nameedit.reset(ctx.channel)
        if error:
            await ctx.send(error)
        # no success message since a success means we have deleted the channel

    @commands.has_permissions(manage_channels=True)
    @commands.command(
        brief='Reset the **entire** server.', name='reset-server'
    )
    async def reset_server(self, ctx: Ctx):
        """Resets the entire server - use with extreme caution.

        This will reset every division category, every division role, the
        follow-up category, the participant role, the kick out on sight role
        and the in break role.

        Example: `{{pre}}reset-server`
        """
        async with ctx.typing():
            await nameedit.reset_guild(ctx.guild)

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
            await roles.mass_role(role, users)
        await ctx.send('Done :thumbsup:')

    @commands.command(brief='How many members a role has.')
    async def members(self, ctx, *, role: discord.Role):
        """Check how many people have a role.

        Example: `{{pre}}members @some-role`.
        """
        await ctx.send(f'{len(role.members)} people have that role.')

    @commands.command(
        brief='Clear a role from people.', name='clear-role'
    )
    @commands.has_permissions(manage_roles=True)
    async def clear_role(self, ctx: Ctx, role: discord.Role):
        """Remove every user from a role.

        Example: `{{pre}}clear-role @Division E`
        """
        async with ctx.typing():
            await roles.mass_un_role(role)
        await ctx.send('Done :thumbsup:')
