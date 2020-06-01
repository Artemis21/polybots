"""Interface between the players cog and the sheets API wrapper."""
import typing

import discord
from discord.ext.commands import Context

from tools import sheetsapi
from tools.paginator import TextPaginator


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


async def get_code_command(ctx: Context, player: sheetsapi.StaticPlayer):
    """Command to find a player's code."""
    await ctx.send(f'Code for **{player.discord_name}**:')
    await ctx.send(f'`{player.friend_code}`')


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
