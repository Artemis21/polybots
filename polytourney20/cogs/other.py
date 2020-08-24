"""Miscellaneous other commands."""
import typing

from discord.ext import commands
import discord

from tools import archiver
from tools.checks import admin


class Other(commands.Cog):
    """Miscellaneous other commands."""

    def __init__(self, bot: commands.Bot):
        """Store the bot."""
        self.bot = bot

    @commands.command(brief='Archive channel.')
    @admin()
    async def archive(self, ctx, search: str):
        """Archive channels by search.

        Returns a links to HTML files. Uploads any images to Imgur so they
        won't be lost if the channel is deleted.

        Example: `{{pre}}archive -finalists`
        """
        async with ctx.typing():
            links = await archiver.archive_channels(search)
            await ctx.send(links)
