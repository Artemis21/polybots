"""Paginator utility."""
import typing

import discord
from discord.ext.commands import Context


class Paginator:
    """Base class for paginators."""

    def __init__(self, ctx: Context, max_page: int):
        """Prepare the paginator."""
        self.ctx = ctx
        self.position = 0
        self.max_page = max_page
        self.message = None
        ctx.bot.add_listener(self.on_reaction_add)

    async def setup(self):
        """Async setup."""
        self.message = await self.send()
        if self.max_page > 0:
            await self.message.add_reaction('◀')
            await self.message.add_reaction('▶')

    async def send(self):
        """Send page 1 and return the message."""
        raise NotImplementedError('Send function must be implemented.')

    async def edit(self):
        """Edit message to show a new page."""
        raise NotImplementedError('Edit function must be implemented.')

    async def back(self):
        """Go to the previous page."""
        if self.position > 0:
            self.position -= 1
            await self.edit()

    async def forward(self):
        """Go to the next page."""
        if self.position < self.max_page:
            self.position += 1
            await self.edit()

    async def on_reaction_add(
            self, reaction: discord.Reaction, user: discord.User):
        """Process a reaction being added."""
        if user != self.ctx.author:
            return
        if reaction.message.id != self.message.id:
            return
        if reaction.emoji == '▶':
            await self.forward()
        elif reaction.emoji == '◀':
            await self.back()
        await reaction.remove(user)


class FieldPaginator(Paginator):
    """Paginator where entries are embed fields."""

    def __init__(
            self, ctx: Context, title: str, fields: typing.Dict[str, str],
            description: str = '', colour: int = 0x7289DA,
            per_page: int = 10):
        """Set up the paginator."""
        self.base_embed = discord.Embed(
            title=title, description=description, colour=colour
        )
        self.pages = [{}]
        for name, value in fields.items():
            if len(self.pages[-1]) >= per_page:
                self.pages.append({})
            self.pages[-1][name] = value
        super().__init__(ctx, len(self.pages) - 1)

    async def send(self):
        """Send the embed."""
        e = self.base_embed.copy()
        for name, value in self.pages[0].items():
            e.add_field(name=name, value=value, inline=False)
        e.set_footer(text=f'Page 1 of {len(self.pages)}.')
        return await self.ctx.send(embed=e)

    async def edit(self):
        """Edit the embed."""
        e = self.base_embed.copy()
        for name, value in self.pages[self.position].items():
            e.add_field(name=name, value=value, inline=False)
        e.set_footer(text=f'Page {self.position + 1} of {len(self.pages)}.')
        await self.message.edit(embed=e)


class TextPaginator(Paginator):
    """Paginator where entries are lines of text."""

    def __init__(
            self, ctx: Context, lines: typing.List[str], header: str = '',
            footer: str = '', per_page: int = 40):
        """Set up the paginator."""
        pages = [[]]
        for line in lines:
            if len(pages[-1]) > per_page:
                pages.append([])
            pages[-1].append(line)
        self.pages = [
            '{header}\n{body}\n{footer}\n*Page {page} of {pages}*'.format(
                header=header, body=('\n'.join(lines) or '*None*'),
                footer=footer, page=page + 1, pages=len(pages)
            ) for page, lines in enumerate(pages)
        ]
        super().__init__(ctx, len(self.pages) - 1)

    async def send(self):
        """Send the message."""
        return await self.ctx.send(self.pages[self.position])

    async def edit(self):
        """Edit the message."""
        await self.message.edit(content=self.pages[self.position])
