"""A base class for object lists."""
from functools import lru_cache
import json
import typing

import discord
from discord.ext import commands


@lru_cache(8)
def load_data(object_type: str) -> typing.Dict:
    """Load data from the file."""
    with open(f'data/{object_type}s.json') as f:
        return json.load(f)


@lru_cache(8)
def list_all(object_type: str) -> str:
    """List short codes and names for a list."""
    lines = []
    for unit in load_data(object_type).values():
        lines.append('`{code}`: {name}'.format(**unit))
    return '\n'.join(lines)


@lru_cache(32)
def embed(
        object_type: str, object_name: str,
        ignore_fields: typing.Tuple[str] = (),
        footer_fields: typing.Tuple[str] = ()
        ) -> discord.Embed:
    """Create an embed to display object information."""
    obj = load_data(object_type)[object_name]
    e = discord.Embed(
        title=obj['name'], description=obj['description'], colour=0xff67be
    )
    if 'image' in obj:
        e.set_thumbnail(url=obj['image'])
    footer_fields = ['code', *footer_fields]
    e.set_footer(text=' | '.join(
        f'{field.title()}: {obj[field]}' for field in footer_fields
    ))
    ignore_fields = [*footer_fields, 'name', 'description', 'image']
    for field in obj:
        if field not in ignore_fields:
            value = obj[field]
            if isinstance(value, list):
                parts = value or ['None']
            else:
                parts = [value]
            value = ', '.join(
                str(part).title().replace('_', ' ') for part in parts
            )
            e.add_field(name=field.title(), value=value)
    return e


@lru_cache(1024)
def lookup(object_type: str, search: str) -> typing.Optional[str]:
    """Lookup an object by user search."""
    data = load_data(object_type)
    search = search.lower().replace(' ', '_').replace('-', '_')
    for full_name in data:
        if search == data[full_name]['code']:
            return full_name
    possible = []
    for full_name in data:
        if search in full_name:
            possible.append(full_name)
    if len(possible) == 1:
        return possible[0]
    elif possible:
        raise commands.BadArgument(
            f'Multiple {object_type}s found by search "{search}". '
            f'Try being more specific, or use a {object_type} code.'
        )
    else:
        raise commands.BadArgument(
            f'Could not find any {object_type}s by search "{search}". '
            f'Try being less specific, or use a {object_type} code.'
        )


class ObjectConverter(commands.Converter):
    """A discord.py converter for looking up and displaying objects."""

    embed_opts = {
        'unit': {
            'footer_fields': ('type',)
        },
        'skill': {}
    }

    def __init__(self, object_type: str):
        """Define the type of object this converter will convert."""
        self.object_type = object_type

    async def convert(
            self, ctx: commands.Context, argument: str
            ) -> typing.Optional[discord.Embed]:
        """Convert an argument."""
        return embed(
            self.object_type, lookup(self.object_type, argument),
            **type(self).embed_opts[self.object_type]
        )
