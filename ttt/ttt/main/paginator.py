"""A reaction pagination utility."""
import discord
from discord.ext import commands

from . import config


class Paginator:
    """A base class for reaction paginators."""

    def __init__(self, ctx: commands.Context, page_count: int):
        """Store the paginator settings."""
        self.ctx = ctx
        self.position = 0
        self.page_count = page_count
        self.message = None
        ctx.bot.add_listener(self.on_reaction_add)

    async def setup(self):
        """Set up the paginator message."""
        self.message = await self.send(self.ctx.channel)
        await self.message.add_reaction('◀')
        await self.message.add_reaction('▶')

    async def send(self, channel: discord.abc.Messageable) -> discord.Message:
        """Send the first page to a channel and return the message."""
        raise NotImplementedError

    async def edit(self, message: discord.Message, page: int):
        """Edit the message to show a specific page number."""
        raise NotImplementedError

    def back(self):
        """Go to the previous page."""
        self.position = max(0, self.position - 1)

    def forward(self):
        """Go to the next page."""
        self.position = min(self.page_count - 1, self.position + 1)

    async def on_reaction_add(
            self, reaction: discord.Reaction, user: discord.User):
        """Process a reaction being added."""
        if reaction.message.id != self.message.id:
            return
        if user != self.ctx.author:
            return
        if reaction.emoji == '▶':
            self.forward()
        elif reaction.emoji == '◀':
            self.back()
        await self.edit(self.message, self.position)
        await reaction.remove(user)


class EmbedDescriptionPaginator(Paginator):
    """A paginator where the paginated lines are in an embed field."""

    def __init__(
            self, ctx: commands.Context, *, title: str, lines: list[str],
            max_lines: int = 10, header: str = ''):
        """Set up the paginator pages."""
        self.base = discord.Embed(title=title, colour=config.COL_ACCENT)
        pages = [[]]
        for line in lines:
            if len(pages[-1]) >= max_lines:
                pages.append([])
            pages[-1].append(line)
        self.pages = [header + '\n'.join(page) for page in pages]
        super().__init__(ctx, len(pages))

    async def send(self, channel: discord.abc.Messageable) -> discord.Message:
        """Send the first page to a channel."""
        embed = self.base.copy()
        embed.description = self.pages[0] or '*Such empty*'
        embed.set_footer(text=f'Page 1 of {len(self.pages)}.')
        return await channel.send(embed=embed)

    async def edit(self, message: discord.Message, page: int):
        """Edit the message to show a page."""
        embed = self.base.copy()
        embed.description = self.pages[page] or '*Such empty*'
        embed.set_footer(text=f'Page {page + 1} of {len(self.pages)}.')
        await message.edit(embed=embed)


class CodeBlockPaginator(Paginator):
    """A paginator where the paginated lines are in a code block."""

    def __init__(
            self, ctx: commands.Context, *, title: str, lines: list[str],
            max_lines: int = 10, header: str = ''):
        """Set up the paginator pages."""
        self.base = (
            f'{title}```md\n# {header}\n\n{{body}}\n\n> Page '
            '{page} of {pages}```'
        )
        pages = [[]]
        for line in lines:
            if len(pages[-1]) >= max_lines:
                pages.append([])
            pages[-1].append(line)
        self.pages = ['\n'.join(page) for page in pages]
        super().__init__(ctx, len(pages))

    async def send(self, channel: discord.abc.Messageable) -> discord.Message:
        """Send the first page to a channel."""
        message = self.base.format(
            body=self.pages[0] or '*Such empty...*',
            page=1,
            pages=len(self.pages)
        )
        return await channel.send(message)

    async def edit(self, message: discord.Message, page: int):
        """Edit the message to show a page."""
        content = self.base.format(
            body=self.pages[page] or '*Such empty...*',
            page=page + 1,
            pages=len(self.pages)
        )
        await message.edit(content=content)
