"""Commands for managing and sending tags."""
import discord
from discord.ext import commands

from ..main import checks, config
from ..main.paginator import EmbedDescriptionPaginator
from ..models.tags import Tag


class Tags(commands.Cog):
    """Commands for managing and sending tags."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the client."""
        self.bot = bot

    @commands.command(brief='Create a tag.', name='new-tag')
    @checks.manager()
    async def new_tag(self, ctx: commands.Context, name: str, *, content: str):
        """Create a new tag.

        Example: `{{pre}}new-tag example This is an example tag.`
        """
        if Tag.get_or_none(Tag.names == name):
            await ctx.send(f'A tag called "{name}" already exists.')
        else:
            Tag.create(names=[name], content=content)
            await ctx.send(f'Created tag "{name}".')

    @commands.command(brief='Send a tag.', name='tag')
    async def tag(self, ctx: commands.Context, *, tag: Tag):
        """Send a tag by name.

        Example: `{{pre}}tag tag name`
        """
        a = Tag.names == 'foo'
        b = Tag.uses == 1
        tag.uses += 1
        tag.save()
        await ctx.message.delete()
        await ctx.send(tag.content)

    @commands.command(brief='Add a tag alias.', name='alias-tag')
    @checks.manager()
    async def alias_tag(
            self, ctx: commands.Context, tag: Tag, new_name: str):
        """Add an alias to an existing tag.

        Example: `{{pre}}alias-tag example xmpl`
        """
        if Tag.get_or_none(Tag.names == new_name):
            await ctx.send(f'A tag called "{new_name}" already exists.')
        else:
            tag.names = [*tag.names, new_name]
            tag.save()
            await ctx.send(f'Added "{new_name}" as an alias of "{tag}".')

    @commands.command(
        brief='Delete a tag.', name='delete-tag', aliases=['del-tag'])
    @checks.manager()
    async def delete_tag(self, ctx: commands.Context, *, tag: Tag):
        """Delete an existing tag.

        Example: `{{pre}}delete-tag example`

        Note that this will also delete all aliases. To delete just one alias,
        use `{{pre}}delete-tag-alias`.
        """
        tag.delete_instance()
        await ctx.send('Deleted that tag.')

    @commands.command(
        brief='Delete a tag alias.', name='delete-tag-alias',
        aliases=['del-tag-alias'])
    @checks.manager()
    async def delete_tag_alias(self, ctx: commands.Context, alias: str):
        """Remove an alias from a tag.

        Example: `{{pre}}del-tag-alias xmpl`
        """
        if tag := Tag.get_or_none(Tag.names == alias):
            if len(tag.names) > 1:
                tag.names = [name for name in tag.names if name != alias]
                tag.save()
                await ctx.send('Removed that alias.')
            else:
                await ctx.send(
                    'That is the only alias that tag has. Did you mean '
                    f'`{ctx.prefix}delete-tag`?'
                )
        else:
            await ctx.send(f'No tag found by name "{alias}".')

    @commands.command(
        brief='List all tags.', name='list-tags', aliases=['tags']
    )
    async def list_tags(self, ctx: commands.Context):
        """List all existing tags.

        Example: `{{pre}}list-tags`
        """
        lines = []
        for tag in Tag.select().order_by(-Tag.uses):
            names = '/'.join(tag.names)
            lines.append(f'**{names}:** {tag.uses} uses')
        await EmbedDescriptionPaginator(
            ctx, title='Tags', lines=lines, header=''
        ).setup()

    @commands.command(brief='Info on a tag.', name='tag-info')
    async def tag_info(self, ctx: commands.Context, *, tag: Tag):
        """View information on a tag.

        Example: `{{pre}}tag-info example tag`
        """
        await ctx.send(embed=discord.Embed(
            title='/'.join(tag.names),
            description=tag.content,
            colour=config.COL_ACCENT
        ).set_footer(text=f'{tag.uses} uses'))
