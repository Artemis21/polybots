"""Interface between the players cog and the sheets API wrapper."""
import typing

import discord
from discord.ext.commands import Context

from tools import sheetsapi, hastebin
from tools.paginator import TextPaginator
from tools.config import Config


config = Config()


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


def list_players(
        check: typing.Callable,
        sort: typing.Callable = lambda p: (-p.wins, p.losses)
        ) -> typing.List[str]:
    """List all players, with an optional filter."""
    players = sheetsapi.get_players()
    players = list(filter(check, players))
    players.sort(key=sort)
    lines = []
    for n, player in enumerate(players):
        lines.append(
            f'**#{n + 1}:** {player.discord_name} *({player.wins}W/'
            f'{player.losses}L)*'
        )
    return lines


async def leaderboard_command(ctx: Context):
    """Command to view the leaderboard."""
    async with ctx.typing():
        lines = list_players(lambda p: True)
    await TextPaginator(
        ctx, lines, '**__Leaderboard__**', per_page=20
    ).setup()


async def all_on_level_command(ctx: Context, level: int):
    async with ctx.typing():
        lines = list_players(lambda p: p.wins == level)
    await TextPaginator(
        ctx, lines, f'**__Level {level} Players__**', per_page=20
    ).setup()


async def on_level_needs_game_command(ctx: Context, level: int):
    async with ctx.typing():
        lines = list_players(
            lambda p: p.needs_games and (p.wins == level),
            sort=lambda p: p.games_in_progress
        )
    await TextPaginator(
        ctx, lines, f'**__Level {level} players needing games__**',
        per_page=20
    ).setup()


async def give_all_role(ctx: Context, role: discord.Role):
    """Give all players a role."""
    async with ctx.typing():
        players = sheetsapi.get_players()
        added = 0
        already = 0
        not_found = []
        for player in players:
            main_name = '#'.join(
                player.discord_name.split('#')[:-1]
            ) or player.discord_name
            user = discord.utils.get(
                config.guild.members, name=main_name
            )
            if user:
                if role in user.roles:
                    already += 1
                else:
                    await user.add_roles(role)
                    added += 1
            else:
                not_found.append(player.discord_name)
        url = hastebin.upload('\n'.join(not_found))
        await ctx.send(
            f'Gave role to {added} participants(s), {already} '
            f'participants(s) already had it and {len(not_found)} '
            f'participant(s) could not be found on Discord (list here: '
            f'{url}).'
        )
