"""Commands for viewing and updating player profiles."""
import typing

import discord
from discord.ext import commands

from main import models, timezones
from main.tribes import TribeList


class Players(commands.Cog):
    """Commands for viewing and updating player profiles."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot

    @commands.command(brief='View the leaderboard.', aliases=['lb'])
    async def leaderboard(self, ctx: commands.Context):
        """Get the leaderboard.

        Example: `{{pre}}leaderboard`
        """
        data = models.Player.get_leaderboard()
        lines = []
        n = 0
        joint_count = 0
        previous_score = None
        for discord_id, wins in data:
            if previous_score != wins:
                n += joint_count + 1
                joint_count = 0
            else:
                joint_count += 1
            previous_score = wins
            lines.append(f'**#{n}** <@{discord_id}> *({wins} wins)*')
        await ctx.send(embed=discord.Embed(
            title='Diplotopia Leaderboard',
            description='\n'.join(lines) or '*There\'s nothing here!*',
            colour=0xF58F29
        ))

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
        player = models.Player.get_player(user.id)
        games = len(models.GameMember.select().where(
            models.GameMember.player == player
        ))
        tz = player.utc_offset or 'Unknown'
        ign = player.in_game_name or 'Unknown'
        embed = discord.Embed(
            title=user.display_name,
            description=(
                f'In-game name: {ign}\nTimezone: {tz}\n'
                f'Tribes: {player.tribes}\nGames: {games}\n'
                f'Wins: {player.wins}'
            ),
            colour=0xF58F29
        )
        embed.set_thumbnail(url=user.avatar_url)
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
        player = models.Player.get_player(ctx.author.id)
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
        player = models.Player.get_player(ctx.author.id)
        player.tribes -= tribes
        player.save()
        await ctx.send('Removed from your tribes :thumbsup:')

    @commands.command(
        brief='Set your name.', name='set-name', aliases=['name', 'ign']
    )
    async def set_name(self, ctx: commands.Context, *, name: str):
        """Set your in-game name.

        Example: `{{pre}}ign artemisdev`
        """
        player = models.Player.get_player(ctx.author.id)
        player.in_game_name = name
        player.save()
        await ctx.send('Updated your in-game name :thumbsup:')

    @commands.command(
        brief='Set your timezone.', name='set-timezone',
        aliases=['timezone', 'set-tz', 'tz']
    )
    async def set_timezone(
            self, ctx: commands.Context, timezone: timezones.Timezone):
        """Set your timezone as a UTC offset.

        Examples:
        `{{pre}}tz UTC+5`
        `{{pre}}tz UTC-1.5`
        `{{pre}}tz UTC+2:30`
        `{{pre}}tz -4`
        """
        player = models.Player.get_player(ctx.author.id)
        player.utc_offset = timezone
        player.save()
        await ctx.send('Updated your timezone :thumbsup:')
