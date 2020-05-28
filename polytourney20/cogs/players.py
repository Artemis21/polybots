"""The cog for getting information on players."""
import typing

from discord.ext import commands
import discord

from tools import players
from tools.checks import admin


class Players(commands.Cog):
    """Commands for getting information on players."""

    def __init__(self, bot: commands.Bot):
        """Store the bot."""
        self.bot = bot

    @commands.command(brief='Look up a player.')
    async def player(self, ctx, *, player: players.PlayerConverter):
        """Look up a player.

        You can do this by Discord name, Discord mention, Polytopia name
        or friend code.
        """
        await players.search_command(ctx, player)

    @commands.command(brief='Get someone\'s friend code.')
    async def code(self, ctx, *, player: players.PlayerConverter):
        """Get a player's friend code."""
        await players.get_code_command(ctx, player)

    @commands.command(brief='View the leaderboard.', aliases=['lb'])
    async def leaderboard(self, ctx):
        """View the leaderboard."""
        await players.leaderboard_command(ctx)

    @commands.command(
        brief='Check if a game has been played.', name='rematch-check',
        aliases=['rematch']
    )
    @admin()
    async def rematchcheck(
            self, ctx, player1: players.PlayerConverter,
            player2: players.PlayerConverter,
            player3: players.PlayerConverter):
        """Check if a game would be a rematch."""
        await players.rematch_check_command(ctx, player1, player2, player3)

    @commands.command(
        brief='Open a game.', name='open-game', aliases=['open']
    )
    @admin()
    async def opengame(
            self, ctx, level: players.level, host: players.PlayerConverter,
            second: players.PlayerConverter, third: players.PlayerConverter):
        """Open a new game (admin only)."""
        await players.open_game_command(ctx, level, host, second, third)

    @commands.command(brief='End a game.', name='win-game', aliases=['win'])
    @admin()
    async def wingame(
            self, ctx, level: players.level, winner: players.PlayerConverter,
            loser1: players.PlayerConverter, loser2: players.PlayerConverter):
        """Open a new game (admin only)."""
        await players.end_game_command(ctx, level, winner, loser1, loser2)
