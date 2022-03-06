"""The meta cog."""
import discord
from discord.ext import commands

from tools.errors import on_command_error
from tools import colours


ABOUT = (
    'GiantBot is a utility bot for the Discord Polytopia Giants League. '
    'It provides utilities for the mods and quick access to the rules.'
)


class Meta(commands.Cog):
    """Commands relating to the bot itself."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the client."""
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Set the help command cog to this one."""
        self.bot.help_command.cog = self

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Send prefix if bot is mentioned."""
        if not message.guild:
            return
        if message.guild.me in message.mentions:
            await message.channel.send(
                f'My prefix is `{self.bot.command_prefix}`.'
            )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Handle an error."""
        await on_command_error(ctx, error)

    @commands.command(brief='About the bot.')
    async def about(self, ctx: commands.Context):
        """Get some information about the bot."""
        embed = discord.Embed(
            title='About',
            description=ABOUT,
            colour=colours.theme()
        )
        embed.set_footer(text='By Artemis (arty.li)')
        embed.set_thumbnail(url=str(ctx.bot.user.avatar))
        await ctx.send(embed=embed)
