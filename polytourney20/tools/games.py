import typing
import random

from discord.ext.commands import Context
import discord

from tools import sheetsapi
from tools.players import get_user
from tools.paginator import TextPaginator
from tools.config import Config


config = Config()


def list_games(
        level: int, fun: typing.Callable, *players: sheetsapi.StaticPlayer):
    """List all games with a filter."""
    games = sheetsapi.all_games(level)
    lines = []

    def filter_fun(game: sheetsapi.Game):
        """Check if a game is to be included."""
        if not fun(game):
            return False
        game_players = (game.player1, game.player2, game.player3)
        return all(
            ((not p) or (p.discord_name in game_players))
            for p in players
        )

    for game in filter(filter_fun, games):
        lines.append(
            f'`{game.id}` **{game.player1}** v **{game.player2}** v '
            f'**{game.player3}**'
        )
    return lines


async def incomplete_games_cmd(
        ctx: Context, level: int,
        player1: typing.Optional[sheetsapi.StaticPlayer],
        player2: typing.Optional[sheetsapi.StaticPlayer]
        ):
    """Command to view incomplete games for some level."""
    lines = list_games(level, lambda game: not game.winner, player1, player2)
    if player1:
        including = f' including {player1.discord_name}'
        if player2:
            including += f' and {player2.discord_name}'
    else:
        including = ''
    name = f'**__Incomplete level {level} games{including}__**'
    await TextPaginator(ctx, lines, name, per_page=20).setup()


async def complete_games_cmd(
        ctx: Context, level: int,
        player1: typing.Optional[sheetsapi.StaticPlayer],
        player2: typing.Optional[sheetsapi.StaticPlayer]
        ):
    """Command to view complete games for some level."""
    lines = list_games(level, lambda game: game.winner, player1, player2)
    if player1:
        including = f' including {player1.discord_name}'
        if player2:
            including += f' and {player2.discord_name}'
    else:
        including = ''
    name = f'**__Complete level {level} games{including}__**'
    await TextPaginator(ctx, lines, name, per_page=20).setup()


async def all_games_cmd(
        ctx: Context, level: int,
        player1: typing.Optional[sheetsapi.StaticPlayer],
        player2: typing.Optional[sheetsapi.StaticPlayer]
        ):
    """Command to view all games for some level."""
    lines = list_games(level, lambda game: True, player1, player2)
    if player1:
        including = f' including {player1.discord_name}'
        if player2:
            including += f' and {player2.discord_name}'
    else:
        including = ''
    name = f'**__All level {level} games{including}__**'
    await TextPaginator(ctx, lines, name, per_page=20).setup()


async def _log_game(level, *players):
    """Announce the opening of a game."""
    if config.log_channel:
        names = []
        users = []
        for player in players:
            names.append(f'**@{player.discord_name}**')
        if users[0]:
            try:
                await users[0].send(
                    f'You have a level {level} game against {names[1]} and '
                    f'{names[2]} to host. Here are their codes, in the order '
                    'you should add them:'
                )
                await users[0].send(players[1].friend_code)
                await users[0].send(players[2].friend_code)
            except discord.Forbidden:
                pass
        await config.log_channel.send(
            f'New level {level} game!\n{names[0]} will host, {names[1]} will '
            f'have second pick and {names[2]} will be last. Please remember '
            'not to pick Bardur, Luxidoor or Kickoo.'
        )


def _rematch_check(
        *players: typing.Tuple[sheetsapi.StaticPlayer]
        ) -> typing.Tuple[str, bool]:
    """Check whether a game would be a rematch and form a message."""
    levels = sheetsapi.rematch_check(
        *[player.discord_name for player in players]
    )
    if not levels:
        return 'That wouldn\'t be a rematch.', False
    if len(levels) == 1:
        return f'That would be a rematch from level {levels[0]}.', True
    else:
        str_levels = ', '.join(map(str, levels[:-1])) + f' and {levels[-1]}'
        return f'That would be a rematch from levels {str_levels}.', True


async def open_game_command(
        ctx: Context, level: int, players: typing.List[sheetsapi.Player]):
    """Command to open a game."""
    async with ctx.typing():
        message, is_rematch = _rematch_check(*players)
    if is_rematch:
        await ctx.send(
            f'{message} Are you sure you want to continue? (`yes` to'
            ' continue, anything else to cancel)'
        )
        response = await ctx.bot.wait_for(
            'message',
            check=lambda m: (
                m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
            )
        )
        if response.content.lower() != 'yes':
            await ctx.send('Cancelling.')
            return
    async with ctx.typing():
        host = min(
            players, key=lambda player: (
                player.host / max(player.total_games, 1),
                player.elo,
                random.randrange(1000)
            )
        )
        second = min(
            [player for player in players if player != host],
            key=lambda player: (
                player.second / max(player.total_games, 1),
                player.elo,
                random.randrange(1000)
            )
        )
        third = [p for p in players if p not in (host, second)][0]
        sheetsapi.create_game(
            level, host.discord_name, second.discord_name, third.discord_name
        )
        await _log_game(level, host, second, third)
    await ctx.send('Game created!')


async def open_many_command(
        ctx: Context, level: int,
        games: typing.List[typing.List[sheetsapi.StaticPlayer]]):
    """Command to open multiple games."""
    async with ctx.typing():
        sheetsapi.create_games(
            level, [
                [player.discord_name for player in game] for game in games
            ]
        )
        for game in games:
            await _log_game(level, *game)
    await ctx.send('Games created!')


async def rematch_check_command(
        ctx: Context, player1: sheetsapi.StaticPlayer,
        player2: sheetsapi.StaticPlayer, player3: sheetsapi.StaticPlayer):
    """Command to check if a game exists."""
    async with ctx.typing():
        message, _is_rematch = _rematch_check(player1, player2, player3)
    await ctx.send(message)


async def lose(
        ctx: Context, game: typing.Tuple[int], player: sheetsapi.StaticPlayer
        ):
    """Command to eliminate a player from a game."""
    async with ctx.typing():
        message = sheetsapi.eliminate_player(*game, player.discord_name)
    await ctx.send(message)


async def win_command(
        ctx: Context, game: typing.Tuple[int],
        player: sheetsapi.StaticPlayer):
    """Command to mark a player as having won a game."""
    async with ctx.typing():
        message = sheetsapi.award_win(*game, player.discord_name)
    await ctx.send(message)


async def get_game_command(ctx: Context, row: typing.Tuple[int]):
    """Command to display a game in an embed."""
    game = sheetsapi.get_game(*row)
    if not game:
        await ctx.send('That is not a valid game.')
        return
    e = discord.Embed(
        title=f'Level {game.level} Game {game.id}',
        description=(
            'This game is over.' if game.winner
            else 'This game is in progress.'
        )
    )
    e.add_field(name='Host', value=game.player1)
    e.add_field(name='Second Pick', value=game.player2)
    e.add_field(name='Third Pick', value=game.player3)
    if game.winner:
        e.add_field(name='Winner', value=f'**{game.winner}**')
    elif game.loser2:
        e.add_field(name='Eliminated', value=f'**{game.loser2}**')
    await ctx.send(embed=e)


async def search_game_command(
        ctx: Context, level: int, player1: sheetsapi.StaticPlayer,
        player2: sheetsapi.StaticPlayer, player3: sheetsapi.StaticPlayer
        ):
    """Command to search for a game by level and players."""
    row = sheetsapi.find_game(
        level, player1.discord_name, player2.discord_name,
        player3.discord_name
    )
    if not row:
        await ctx.send('Could not find game.')
        return
    await get_game_command(ctx, (level, row))
