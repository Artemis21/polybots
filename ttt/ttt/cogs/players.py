"""Commands relating to players and their profiles."""
import csv
import io
from typing import Optional

import discord
from discord.ext import commands

from ..main import checks, matchmaking
from ..main.config import (
    BOT_PLAYER_ROLE_ID, TT_REGISTRATION_CLOSE, TT_REGISTRATION_OPEN
)
from ..main.elo_api import EloApiError
from ..main.paginator import CodeBlockPaginator, EmbedDescriptionPaginator
from ..models import League, Player, TribeList


Ctx = commands.Context


def format_waiting_line(player: Player) -> str:
    """Format a player for a line of &waiting."""
    if not player.league:
        team = 'NO TEAM'
    elif player.league == League.NOVA:
        team = 'NOVA'
    else:
        league = 'JR' if player.league == League.JUNIOR else 'PRO'
        team = str(player.team)[:4].upper() + ' ' + league
    game_summary = (
        f'{player.wins} W / {player.losses} L / '
        f'{player.in_progress} IP'
    )
    games = []
    for game_id, position in zip(player.game_ids, player.game_positions):
        games.append(f'{game_id} - {position}')
    games = '; '.join(games)
    return (
        f'* {player.display_name} ({team}): {game_summary}\n'
        f'> {games} \n'
    )


def optional_player_arg(ctx: Ctx, arg: Optional[Player]) -> Player:
    """Return the argument, defaulting to the author."""
    if player := arg or ctx.ttt_player:
        return player
    raise commands.CommandError(
        f'You not registered (`{ctx.prefix}register`).'
    )


class Players(commands.Cog):
    """Commands relating to players and their profiles."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot

    @commands.command(brief='View a player.', aliases=['profile', 'p'])
    @checks.optional_registered()
    async def player(self, ctx: Ctx, *, player: Player = None):
        """View a player's profile (defaults to your own).

        Examples:
        `{{pre}}profile @Artemis`
        `{{pre}}p`
        """
        player = optional_player_arg(ctx, player)
        await ctx.send(embed=player.embed())

    @commands.command(brief='Register yourself.', aliases=['r'])
    @checks.date_range(TT_REGISTRATION_OPEN, TT_REGISTRATION_CLOSE)
    async def register(self, ctx: Ctx):
        """Sign up for the tournament.

        Example: `{{pre}}register`
        """
        player = Player.get_or_none(Player.discord_id == ctx.author.id)
        if player:
            await ctx.send('You are already registered.')
        else:
            player = Player.create(discord_id=ctx.author.id)
            player.reload_from_discord_member(ctx.author)
            try:
                await player.reload_elo_data()
            except EloApiError:
                await ctx.send(
                    'You are not registered with the ELO bot. Do '
                    '`$setname <mobile name>` to register, then '
                    f'`{ctx.prefix}update-profile` to update your profile.'
                )
            role = ctx.guild.get_role(BOT_PLAYER_ROLE_ID)
            await ctx.author.add_roles(role)
            await ctx.send('Registered you!', embed=player.embed())

    @commands.command(brief='View the leaderboard.', aliases=['lb'])
    async def leaderboard(self, ctx: Ctx):
        """View the player leaderboard.

        Example: `{{pre}}lb`
        """
        lines = []
        for n, player in enumerate(Player.leaderboard()):
            lines.append(
                f'`{n + 1:>3} {player.wins:>2} {player.losses:>2} '
                f'{player.total - player.complete:>2}` '
                f'{player.display_name}'
            )
        await EmbedDescriptionPaginator(
            ctx, title='Leaderboard', lines=lines,
            header='**`  #  W  L  I` Player**\n'
        ).setup()

    @commands.command(
        brief='Add to your tribes.', name='add-tribes',
        aliases=['add-tribe', 'at']
    )
    @checks.registered()
    async def add_tribes(self, ctx: commands.Context, *, tribes: TribeList):
        """Add to the list of tribes you own.

        Examples:
        `{{pre}}add-tribes elyrion yad ven l k p`
        `{{pre}}at all`
        """
        ctx.ttt_player.tribes += tribes
        ctx.ttt_player.save()
        await ctx.send('Added to your tribes :thumbsup:')

    @commands.command(
        brief='Remove from your tribes.', name='remove-tribes',
        aliases=['remove-tribe', 'rt']
    )
    @checks.registered()
    async def remove_tribes(self, ctx: Ctx, *, tribes: TribeList):
        """Remove tribes from the list of tribes you own.

        Example: `{{pre}}rt lux pol`
        """
        ctx.ttt_player.tribes -= tribes
        ctx.ttt_player.save()
        await ctx.send('Removed from your tribes :thumbsup:')

    @commands.command(
        brief='Get your ELO bot profile.', name='reload-profile',
        aliases=['rp']
    )
    @checks.optional_registered()
    async def reload_profile(self, ctx: Ctx, *, player: Player = None):
        """Reload your profile from ELO bot.

        This is useful if you have updated your in game name or timezone.
        You can also use this for someone else.

        Examples:
        `{{pre}}rp`
        `{{pre}}rp @Artemis`
        """
        player = optional_player_arg(ctx, player)
        await player.reload_elo_data()
        await ctx.send('Reloaded!')

    @commands.command(brief='Quit the tournament.')
    @checks.caution('quit the tournament')
    @checks.registered()
    async def quit(self, ctx: Ctx):
        """Quit the tournament.

        This cannot be undone. Please use it with caution.

        Example: `{{pre}}quit`
        """
        ctx.ttt_player.delete_instance()
        role = ctx.guild.get_role(BOT_PLAYER_ROLE_ID)
        await ctx.author.remove_roles(role)
        await ctx.send('Unregistered you. Goodbye.')

    @commands.command(brief='List players waiting on a level.', aliases=['w'])
    @checks.manager()
    async def waiting(self, ctx: Ctx, level: int):
        """List players waiting for games on a level.

        `level` should be -1 or higher.

        Example: `{{pre}}waiting 2`
        """
        if level < -1:
            await ctx.send('Level must be at least -1.')
            return
        players = matchmaking.players_waiting_on_level(level)
        lines = []
        last_total = None
        for player in players:
            line = format_waiting_line(player)
            if player.total != last_total:
                header = f'## {player.total} games\n\n'
                last_total = player.total
            else:
                header = ''
            lines.append(header + line)
        await CodeBlockPaginator(
            ctx, title='', header=f'Players waiting on level {level}',
            lines=lines
        ).setup()

    @commands.command(brief='Ping anyone without a timezone.', name='check-tz')
    @checks.manager()
    async def check_timezones(self, ctx: commands.Context):
        """Ping every player who has not set their timezone.

        Example: `{{pre}}check-tz`
        """
        players = list(
            Player.select().where(Player.timezone.is_null(True))
        )
        if not players:
            await ctx.send('All players set their timezone!')
            return
        mentions = [
            ' '.join(f'<@{player.discord_id}>' for player in chunk)
            for chunk in (
                players[start:start + 90]
                for start in range(0, len(players), 90)
            )
        ]
        await ctx.send('The following players have not set their timezone:')
        for chunk in mentions:
            await ctx.send(chunk)

    @commands.command(
        brief='Export players to CSV.', name='export-players', aliases=['ep'])
    @checks.manager()
    async def export_players(self, ctx: commands.Context):
        """Export a list of all players to CSV.

        Includes: ID, mention, name, team, league and timezone.

        Example: `{{pre}}ep`
        """
        file = io.StringIO()
        writer = csv.writer(file)
        writer.writerow([
            'ID', 'Mention', 'Name', 'Team', 'League', 'UTC offset',
            'Wins', 'Losses', 'Incomplete', 'Total Games'
        ])
        for player in Player.leaderboard():
            writer.writerow([
                player.discord_id, f'<@{player.discord_id}>',
                player.display_name, str(player.team), str(player.league),
                float(player.timezone) if player.timezone else 'Unknown',
                player.wins, player.losses,
                player.total - player.complete, player.total
            ])
        file.seek(0)
        await ctx.send(file=discord.File(file, filename='ttt_players.csv'))
