"""Tags cog."""
from discord.ext import commands

from tools import tags
from tools.checks import admin


class Tags(commands.Cog):
    """Tags cog."""

    def __init__(self, bot: commands.Bot):
        """Store the bot."""
        self.bot = bot

    @commands.command(brief='Get a tag.')
    async def tag(self, ctx, *, name: str):
        """Get a tag.

        Example: `{{pre}}tag games`
        """
        await ctx.message.delete()
        await ctx.send(tags.get_tag(name))

    @commands.command(brief='Create a tag.', name='create-tag')
    @admin()
    async def create_tag(self, ctx, name: str, *, content: str):
        """Create a tag.

        Example: `{{pre}}create-tag games Create a game like so:`
        """
        tags.create_tag(name, content)
        await ctx.send('Created!')
