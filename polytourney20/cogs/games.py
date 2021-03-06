"""The cog for viewing and editing games."""
import typing

from discord.ext import commands
import discord

from tools import games
from tools.checks import admin, commands_channel, is_admin, deprecated
from tools.converters import (
    PlayerConverter, StaticPlayerConverter, level_id, game_id, ManyConverter,
    search_player
)


class Games(commands.Cog):
    """Commands for viewing and editing games."""

    def __init__(self, bot: commands.Bot):
        """Store the bot."""
        self.bot = bot

    @commands.command(
        brief='View in progress games.', aliases=['in-progress', 'ip'],
        name='in-progress-games'
    )
    @commands_channel()
    async def in_progress_games(
            self, ctx, level: level_id,
            player: typing.Optional[StaticPlayerConverter]
            ):
        """View all in progress games for a player on a level."""
        if not player:
            player = search_player(
                str(ctx.author), static_only=True, strict=True
            )
            if not player:
                return await ctx.send(
                    'You are not registered for the tournament (if you have '
                    'changed your Discord username since registering, please '
                    'alert a director.).'
                )
        await games.in_progress_games_cmd(ctx, level, player)

    @commands.command(
        brief='View incomplete games.', aliases=['incomplete', 'inc'],
        name='incomplete-games'
    )
    @commands_channel()
    @deprecated(replace='in-progress')
    async def incomplete_games(
            self, ctx, level: level_id,
            player1: typing.Optional[StaticPlayerConverter],
            player2: typing.Optional[StaticPlayerConverter]
            ):
        """View all incomplete games, optionally filtering by player."""
        await games.incomplete_games_cmd(ctx, level, player1, player2)

    @commands.command(
        brief='View complete games.', aliases=['complete'],
        name='complete-games'
    )
    @commands_channel()
    async def complete_games(
            self, ctx, level: level_id,
            player1: typing.Optional[StaticPlayerConverter],
            player2: typing.Optional[StaticPlayerConverter]
            ):
        """View all complete games, optionally filtering by player."""
        await games.complete_games_cmd(ctx, level, player1, player2)

    @commands.command(
        brief='View all games.', aliases=['games'], name='all-games'
    )
    @commands_channel()
    async def all_games(
            self, ctx, level: level_id,
            player1: typing.Optional[StaticPlayerConverter],
            player2: typing.Optional[StaticPlayerConverter]
            ):
        """View all games, optionally filtering by player."""
        await games.all_games_cmd(ctx, level, player1, player2)

    @commands.command(brief='View a game.')
    @commands_channel()
    async def game(self, ctx, game: game_id):
        """View details on a specific game."""
        await games.get_game_command(ctx, game)

    @commands.command(
        brief='Search for a game.', name='search-game', aliases=['search']
    )
    @commands_channel()
    async def search_game(
            self, ctx, level: level_id,
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
            self, ctx, level: level_id,
            player1: PlayerConverter,
            player2: PlayerConverter,
            player3: PlayerConverter):
        """Open a new game (admin only)."""
        await games.open_game_command(ctx, level, [player1, player2, player3])

    @commands.command(brief='Open many games.', name='mass-open')
    @admin()
    async def mass_open(
            self, ctx, level: level_id, *, all_players: ManyConverter(
                host=StaticPlayerConverter,
                second=StaticPlayerConverter,
                third=StaticPlayerConverter
            )):
        """Open many games at once (admin only).
        
        Example:
        ```{{pre}}mass-open 5
        @host @second @third
        @player1 @player2 @player3
        @goochie @ramana @artemis```
        Would open 3 level 5 games.
        """
        await games.open_many_command(ctx, level, all_players)

    @commands.command(
        brief='Record a loss.', aliases=['eliminate', 'elim', 'loss']
    )
    @commands_channel()
    async def lose(
            self, ctx, game: game_id, *,
            player: typing.Optional[StaticPlayerConverter]):
        """Mark yourself as having lost a game."""
        author_player = search_player(
            str(ctx.author), static_only=True, strict=True
        )
        if not player:
            if author_player:
                player = author_player
            else:
                return await ctx.send(
                    'You are not registered for the tournament (if you have '
                    'changed your Discord username since registering, please '
                    'alert a director.).'
                )
        if author_player and player.discord_name != author_player.discord_name:
            if not is_admin(ctx.author):
                return await ctx.send(
                    'Only directors may report losses on behalf of others.'
                )
        await games.lose(ctx, game, player)

    @commands.command(brief='Record a win.')
    @admin()
    async def win(
            self, ctx, game: game_id, *, player: StaticPlayerConverter):
        """Mark a player as having won a game (admin only)."""
        await games.win_command(ctx, game, player)

    @commands.command(brief='Get unprocessed results.')
    @admin()
    async def results(self, ctx, *, channel: discord.TextChannel):
        """Get unprocessed results from a text channel (admin only)."""
        await games.get_submitted_result(ctx, channel)
