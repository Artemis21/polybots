"""The meta cog."""
import logging

import discord
from discord.ext import commands

from ..main import checks, config, errors, logs


ABOUT = 'This is a bot to help manage Tiny Tourney Two.'


class Meta(commands.Cog):
    """Commands relating to the bot itself."""

    def __init__(self, bot: commands.Bot):
        """Set the help command cog to this one."""
        self.bot = bot
        self.bot.help_command.cog = self

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Send prefix if bot is mentioned."""
        me = message.guild.me if message.guild else self.bot.user
        if me in message.mentions:
            await message.channel.send(f'My prefix is `{config.BOT_PREFIX}`.')

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Handle an error."""
        await errors.on_command_error(ctx, error)

    @commands.command(brief='About the bot.')
    async def about(self, ctx: commands.Context):
        """Get some information about the bot."""
        embed = discord.Embed(
            title='About',
            description=ABOUT,
            colour=config.COL_ACCENT
        )
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        embed.set_footer(text='By Artemis (artemisdev.xyz).')
        await ctx.send(embed=embed)

    @commands.command(brief='Get tourney logs.')
    @checks.manager()
    async def logs(
            self,
            ctx: commands.Context,
            level: int = logging.INFO,
            limit: int = 1000):
        """Get tournament logs."""
        await ctx.send(
            file=logs.get_logs(max_logs=None), level=level, limit=limit
        )
