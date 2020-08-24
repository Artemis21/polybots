"""Miscellaneous other commands."""
import typing

from discord.ext import commands
import discord

from tools import archiver, pastebin
from tools.checks import admin


class Other(commands.Cog):
    """Miscellaneous other commands."""

    def __init__(self, bot: commands.Bot):
        """Store the bot."""
        self.bot = bot

    @commands.command(brief='Archive a channel.')
    @admin()
    async def archive(
            self, ctx, channel: discord.TextChannel, user: discord.Member):
        """Archive messages in a channel from a user.

        Returns a link to an HTML file. Uploads any images to Imgur so they
        won't be lost if the channel is deleted.

        Example: `{{pre}}archive #c0unse1-finalist @c0unse1`
        """
        async with ctx.typing():
            html = await archiver.archive_channel(channel, user)
            await ctx.send(pastebin.upload(html))
