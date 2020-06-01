"""The cog for viewing and editing games."""
import typing

from discord.ext import commands
import discord

from tools import games
from tools.checks import admin
from tools.converters import StaticPlayerConverter, level, game_id


class Games(commands.Cog):
    """Commands for viewing and editing games."""

    def __init__(self, bot: commands.Bot):
        """Store the bot."""
        self.bot = bot

    @commands.command(
        brief='View incomplete games.', aliases=['incomplete'],
        name='incomplete-games'
    )
    async def incomplete_games(
            self, ctx, level: level,
            player: typing.Optional[StaticPlayerConverter]
            ):
        """View all incomplete games, optionally filtering by player."""
        await games.incomplete_games_cmd(ctx, level, player)

    @commands.command(
            brief='View complete games.', aliases=['complete'],
            name='complete-games'
        )
    async def complete_games(
            self, ctx, level: level,
            player: typing.Optional[StaticPlayerConverter]
            ):
        """View all complete games, optionally filtering by player."""
        await games.complete_games_cmd(ctx, level, player)

    @commands.command(
        brief='View all games.', aliases=['games'], name='all-games'
    )
    async def all_games(
            self, ctx, level: level,
            player: typing.Optional[StaticPlayerConverter]
            ):
        """View all games, optionally filtering by player."""
        await games.all_games_cmd(ctx, level, player)

    @commands.command(brief='View a game.')
    async def game(self, ctx, game: game_id):
        """View details on a specific game."""
        await games.get_game_command(ctx, game)

    @commands.command(
        brief='Search for a game.', name='search-game', aliases=['search']
    )
    async def search_game(
            self, ctx, level: level,
            player1: StaticPlayerConverter,
            player2: StaticPlayerConverter,
            player3: StaticPlayerConverter):
        """Search for a game by level and players."""
        await games.search_game_command(ctx, level, player1, player2, player3)

    @commands.command(
        brief='Check if a game has been played.', name='rematch-check',
        aliases=['rematch']
    )
    @admin()
    async def rematch_check(
            self, ctx, player1: StaticPlayerConverter,
            player2: StaticPlayerConverter,
            player3: StaticPlayerConverter):
        """Check if a game would be a rematch."""
        await games.rematch_check_command(ctx, player1, player2, player3)

    @commands.command(
        brief='Open a game.', name='open-game', aliases=['open']
    )
    @admin()
    async def open_game(
            self, ctx, level: level,
            host: StaticPlayerConverter,
            second: StaticPlayerConverter,
            third: StaticPlayerConverter):
        """Open a new game (admin only)."""
        await games.open_game_command(ctx, level, host, second, third)

    @commands.command(
        brief='Eliminate a player.',
        name='eliminate-player', aliases=['eliminate']
    )
    @admin()
    async def eliminate_player(
            self, ctx, game: game_id, player: StaticPlayerConverter):
        """Mark a player as eliminated from a game (admin only)."""
        await games.eliminate_player_command(ctx, game, player)

