"""Interface between the players cog and the sheets API wrapper."""
import typing
import re

import discord
from discord.ext.commands import Context

from tools import sheetsapi, pastebin
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
    await ctx.send(f'{player.friend_code}')


def escape_md(raw: str) -> str:
    """Escape Discord markdown."""
    return re.sub(r'[_*|`~\\]', lambda m: '\\' + m.group(0), raw)


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
            f'**#{n + 1}:** {escape_md(player.discord_name)} '
            f'*({player.wins}W/{player.losses}L/'
            f'{player.games_in_progress}IP)*'
        )
    return lines


async def leaderboard_command(ctx: Context):
    """Command to view the leaderboard."""
    async with ctx.typing():
        lines = list_players(lambda p: p.wins or p.losses)
    await TextPaginator(
        ctx, lines, '**__Leaderboard__**', per_page=20
    ).setup()


async def all_on_level_command(ctx: Context, level: int):
    async with ctx.typing():
        lines = list_players(lambda p: p.level == level)
    await TextPaginator(
        ctx, lines, f'**__Level {level} Players__**', per_page=20
    ).setup()


def get_user(player: sheetsapi.StaticPlayer) -> discord.Member:
    """Get a member from a player."""
    main_name = '#'.join(
        player.discord_name.split('#')[:-1]
    ) or player.discord_name
    discrim = player.discord_name.split('#')[-1].strip()
    alt_1 = main_name.strip()
    alt_2 = main_name[0].upper() + main_name[1:]
    alt_3 = main_name[0].lower() + main_name[1:]
    for name in (main_name, alt_1, alt_2, alt_3):
        user = discord.utils.get(
            config.guild.members, name=name, discriminator=discrim
        )
        if user:
            break
    return user


async def on_level_needs_game_command(ctx: Context, level: int):
    def check_player(player):
        """Check if a player should be included."""
        if not player.needs_games:
            return False
        if player.level != level:
            return False
        return bool(get_user(player))

    async with ctx.typing():
        lines = list_players(check_player, lambda p: p.total_games)
    await TextPaginator(
        ctx, lines, f'**__Level {level} players needing games__**',
        per_page=20
    ).setup()


async def give_all_role(ctx: Context, role: discord.Role):
    """Give all players a role."""
    async with ctx.typing():
        players = sheetsapi.get_players()
        added = []
        already = []
        not_found = []
        for player in players:
            user = get_user(player)
            if user:
                if role in user.roles:
                    already.append(str(user))
                else:
                    await user.add_roles(role)
                    added.append(str(user))
            else:
                not_found.append(player.discord_name)
        not_found_url = pastebin.upload('\n'.join(not_found))
        participants = [*already, *added]
        participants_url = pastebin.upload('\n'.join(participants))
        await ctx.send(
            f'Gave role to {len(added)} participants(s), {len(already)} '
            f'participants(s) already had it and {len(not_found)} '
            f'participant(s) could not be found on Discord.\n Not found: '
            f'{not_found_url} | Valid participants: {participants_url}.'
        )
