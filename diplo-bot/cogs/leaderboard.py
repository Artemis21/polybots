"""Commands for viewing and updating the leaderboard."""
import typing

import discord
from discord.ext import commands

from main import models


class Leaderboard(commands.Cog):
    """Commands for viewing and updating the leaderboard."""

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
            lines.append(f'**#{n}** <@{discord_id}> *({wins}) wins*')
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
        win_plural = '' if player.wins == 1 else 's'
        embed = discord.Embed(
            title=user.display_name,
            description=f'{player.wins} win{win_plural}',
            colour=0xF58F29
        )
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(brief='Award a win.', aliases=['w', 'winner', 'winners'])
    @commands.has_guild_permissions(administrator=True)
    async def win(
            self, ctx: commands.Context,
            *users: commands.Greedy[discord.Member]):
        """Award a win to one or more users.

        Example: `{{pre}}win @Artemis @Dorian @JBHoTep`
        """
        models.Player.give_many_wins([user.id for user in users])
        await ctx.send('Done!')
