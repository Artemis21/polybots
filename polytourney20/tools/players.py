"""Interface between the players cog and the sheets API wrapper."""
import typing

import discord
from discord.ext.commands import Context, BadArgument, MemberConverter

from tools import sheetsapi
from tools.paginator import TextPaginator


def level(argument: str) -> int:
    """A converter for the game levels."""
    try:
        level = int(argument)
    except ValueError:
        raise BadArgument(f'No such level `{argument}`.')
    if level not in range(10):
        raise BadArgument(f'No such level `{level}`.')
    return level


class PlayerConverter(MemberConverter):
    """Converter for player searches."""

    async def convert(self, ctx: Context, argument: str) -> sheetsapi.Player:
        """Convert a player search argument."""
        try:
            user = await super().convert(ctx, argument)
            searches = [user.name, user.display_name]
        except BadArgument:
            searches = [argument]
        async with ctx.typing():
            possible = sheetsapi.search_player(searches)
        if not possible:
            raise BadArgument(
                f'Could not find player `{argument}`. Try being less '
                'specific, or mentioning a user.'
            )
        elif len(possible) > 1:
            raise BadArgument(
                f'Found multiple players by search `{argument}`. Try being '
                'more specific, or mentioning a user.'
            )
        return possible[0]


async def search_command(ctx: Context, player: sheetsapi.Player):
    """Command to search for a player."""
    e = discord.Embed(
        title=player.discord_name,
        description=f'`{player.friend_code}`',
        colour=0xD92B2B
    )
    e.add_field(name='Polytopia Name', value=player.polytopia_name)
    e.add_field(name='ELO', value=player.elo)
    games = (
        f'{player.total_games} ({player.wins} wins, '
        f'{player.losses} losses, {player.games_in_progress} in '
        'progress)'
    )
    e.add_field(name='Games', value=games)
    e.add_field(
        name='Needs games?',
        value=('Yes' if player.needs_games else 'No')
    )
    hosted = (
        f'{player.host} (2nd in {player.second}, 3rd in '
        f'{player.third})'
    )
    e.add_field(name='Hosted', value=hosted)
    await ctx.send(embed=e)


async def get_code_command(ctx: Context, player: sheetsapi.Player):
    """Command to find a player's code."""
    await ctx.send(f'Code for **{player.discord_name}**:')
    await ctx.send(f'`{player.friend_code}`')


async def open_game_command(
        ctx: Context, level: int, host: sheetsapi.Player,
        second: sheetsapi.Player, third: sheetsapi.Player):
    """Command to open a game."""
    async with ctx.typing():
        sheetsapi.create_game(
            level, host.discord_name, second.discord_name, third.discord_name
        )
    await ctx.send('Game created!')


async def rematch_check_command(
        ctx: Context, player1: sheetsapi.Player,
        player2: sheetsapi.Player, player3: sheetsapi.Player):
    """Command to check if a game exists."""
    async with ctx.typing():
        levels = sheetsapi.rematch_check(
            player1.discord_name, player2.discord_name,
            player3.discord_name
        )
    if not levels:
        await ctx.send('That wouldn\'t be a rematch.')
    if len(levels) == 1:
        await ctx.send(f'That would be a rematch from level {levels[0]}.')
    else:
        str_levels = ', '.join(map(str, levels[:-1])) + f' and {levels[-1]}'
        await ctx.send(f'That would be a rematch from levels {str_levels}.')


async def end_game_command(
        ctx: Context, level: int, winner: sheetsapi.Player,
        loser1: sheetsapi.Player, loser2: sheetsapi.Player):
    """Command to mark a game as complete."""
    async with ctx.typing():
        sheetsapi.set_result(
            level, winner.discord_name, loser1.discord_name,
            loser2.discord_name
        )
    await ctx.send('Win recorded!')


async def leaderboard_command(ctx: Context):
    """Command to view the leaderboard."""
    async with ctx.typing():
        players = sheetsapi.get_players()
        players.sort(key=lambda player: (-player.wins, player.losses))
        lines = []
        for n, player in enumerate(players):
            lines.append(
                f'**#{n + 1}:** {player.discord_name} *({player.wins}W/'
                f'{player.losses}L)*'
            )
    await TextPaginator(
        ctx, lines, '**__Leaderboard__**', per_page=20
    ).setup()
