"""Commands for viewing and updating player profiles."""
import typing

import discord
from discord.ext import commands

from ..models import GameMember, Player, Timezone, TribeList


class Players(commands.Cog):
    """Commands for viewing and updating player profiles."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot

    @commands.command(brief='View a profile.', aliases=['profile', 'p'])
    async def player(
            self, ctx: commands.Context, *,
            user: typing.Optional[discord.Member] = None):
        """Get a player's profile (defaults to your own).

        Examples:
        `{{pre}}player @Artemis`
        `{{pre}}p`
        """
        user = user or ctx.author
        player = Player.get_player(user.id)
        games = len(GameMember.select().where(
            GameMember.player == player
        ))
        tz = player.utc_offset or 'Unknown'
        steam = player.steam_name or 'Unknown'
        mobile = player.mobile_name or 'Unkown'
        embed = discord.Embed(
            title=user.display_name,
            description=(
                f'Steam name: {steam}\nMobile name: {mobile}\n'
                f'Timezone: {tz}\nTribes: {player.tribes}\nGames: {games}\n'
            ),
            colour=0xF58F29
        )
        embed.set_thumbnail(url=str(user.avatar))
        await ctx.send(embed=embed)

    @commands.command(
        brief='Add to your tribes.', name='add-tribes',
        aliases=['add-tribe', 'at']
    )
    async def add_tribes(self, ctx: commands.Context, *, tribes: TribeList):
        """Add to the list of tribes you own.

        Examples:
        `{{pre}}add-tribes elyrion yad ven l k p`
        `{{pre}}at all`
        """
        player = Player.get_player(ctx.author.id)
        player.tribes += tribes
        player.save()
        await ctx.send('Added to your tribes :thumbsup:')

    @commands.command(
        brief='Remove from your tribes.', name='remove-tribes',
        aliases=['remove-tribe', 'rt']
    )
    async def remove_tribes(self, ctx: commands.Context, *, tribes: TribeList):
        """Remove tribes from the list of tribes you own.

        Example: `{{pre}}rt lux pol`
        """
        player = Player.get_player(ctx.author.id)
        player.tribes -= tribes
        player.save()
        await ctx.send('Removed from your tribes :thumbsup:')

    @commands.command(
        brief='Set your mobile name.', name='mobile-name',
        aliases=['mn']
    )
    async def mobile_name(self, ctx: commands.Context, *, name: str):
        """Set your in-game name for mobile.

        Example: `{{pre}}mn artemisdev`
        """
        player = Player.get_player(ctx.author.id)
        player.mobile_name = name
        player.save()
        await ctx.send('Updated your mobile name :thumbsup:')

    @commands.command(
        brief='Set your steam name.', name='steam-name',
        aliases=['sn']
    )
    async def steam_name(self, ctx: commands.Context, *, name: str):
        """Set your in-game name for steam.

        Example: `{{pre}}sn artemisdev`
        """
        player = Player.get_player(ctx.author.id)
        player.steam_name = name
        player.save()
        await ctx.send('Updated your steam name :thumbsup:')

    @commands.command(
        brief='Set your timezone.', name='set-timezone',
        aliases=['timezone', 'set-tz', 'tz']
    )
    async def set_timezone(
            self, ctx: commands.Context, timezone: Timezone):
        """Set your timezone as a UTC offset.

        Examples:
        `{{pre}}tz UTC+5`
        `{{pre}}tz UTC-1.5`
        `{{pre}}tz UTC+2:30`
        `{{pre}}tz -4`
        """
        player = Player.get_player(ctx.author.id)
        player.utc_offset = timezone
        player.save()
        await ctx.send('Updated your timezone :thumbsup:')

    @commands.command(
        brief='Search a player by ign.', aliases=['lookup', 's']
    )
    async def search(self, ctx: commands.Context, *, in_game_name: str):
        """Search for a player by their in-game name (steam or mobile).

        Example: `{{pre}}search artemisdev`
        """
        search = in_game_name.lower()
        matches = list(Player.select().where(
            (Player.mobile_name ** f'%{search}%')
            | (Player.steam_name ** f'%{search}%')
        ))
        if not matches:
            await ctx.send(
                f'No player found by in-game name `{in_game_name}`.'
            )
            return
        lines = []
        for match in matches:
            name_matches = []
            if match.mobile_name and search in match.mobile_name.lower():
                name_matches.append(f'**{match.mobile_name}** (mobile)')
            if match.steam_name and search in match.steam_name.lower():
                name_matches.append(f'**{match.steam_name}** (steam)')
            names = ' or '.join(name_matches)
            lines.append(
                f'<@{match.discord_id}> - {names}')
        await ctx.send(embed=discord.Embed(
            title='Possible matches',
            description='\n'.join(lines),
            colour=0xF58F29
        ))
