"""The cog for getting information on players."""
import typing

from discord.ext import commands
import discord

from tools import players
from tools.checks import admin
from tools.converters import PlayerConverter, StaticPlayerConverter, level


class Players(commands.Cog):
    """Commands for getting information on players."""

    def __init__(self, bot: commands.Bot):
        """Store the bot."""
        self.bot = bot

    @commands.command(brief='Look up a player.')
    async def player(self, ctx, *, player: PlayerConverter):
        """Look up a player.

        You can do this by Discord name, Discord mention, Polytopia name
        or friend code.
        """
        await players.search_command(ctx, player)

    @commands.command(
        brief='Get someone\'s friend code.', name='friend-code',
        aliases=['code']
    )
    async def friend_code(self, ctx, *, player: StaticPlayerConverter):
        """Get a player's friend code."""
        await players.get_code_command(ctx, player)

    @commands.command(brief='View the leaderboard.', aliases=['lb'])
    async def leaderboard(self, ctx):
        """View the leaderboard."""
        await players.leaderboard_command(ctx)
