"""The cog for getting information on players."""
import typing

from discord.ext import commands
import discord

from tools import players
from tools.checks import admin
from tools.converters import PlayerConverter, StaticPlayerConverter, level_id


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

    @commands.command(
        brief='View players on a level.', name='players-on-level',
        aliases=['level']
    )
    async def players_on_level(self, ctx, level: level_id):
        """Get a list of players currently on some level."""
        await players.all_on_level_command(ctx, level)

    @commands.command(
        brief='See who needs games.', name='needs-games', aliases=['waiting']
    )
    @admin()
    async def needs_games(self, ctx, level: level_id):
        """See who is waiting for games on some level."""
        await players.on_level_needs_game_command(ctx, level)
