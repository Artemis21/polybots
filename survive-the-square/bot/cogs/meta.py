"""The meta cog."""
import datetime

import discord
from discord.ext import commands

from ..main import config, errors


ABOUT = 'A bot to manage Survive the Square games.'


def timedelta_to_ms(time: datetime.timedelta) -> int:
    """Get the number of miliseconds in a timedelta (ignoring days)."""
    return round(time.seconds * 1e3 + time.microseconds / 1e3)


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
            await message.channel.send(f'My prefix is `{config.PREFIX}`.')

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
            colour=0x45b3e0
        )
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(brief='Get a pong.')
    async def ping(self, ctx: commands.Context):
        """See how fast the bot can respond."""
        now = datetime.datetime.now()
        recieve_time = timedelta_to_ms(now - ctx.message.created_at)
        response = await ctx.send(
            f'Pong!\nRecieve time: `{recieve_time}ms`'
        )
        initial_recieve = now
        now = datetime.datetime.now()
        roundtrip_time = timedelta_to_ms(now - initial_recieve)
        response_time = timedelta_to_ms(response.created_at - initial_recieve)
        await response.edit(content=(
            f'Pong!\nRecieve time: `{recieve_time}ms`'
            f'\nResponse time: `{response_time}ms`'
            f'\nResponse roundtrip: `{roundtrip_time}ms`'
        ))
