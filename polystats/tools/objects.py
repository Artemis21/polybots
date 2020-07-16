"""A base class for object lists."""
from functools import lru_cache
import json
import typing

import discord
from discord.ext import commands


def neaten(raw: str) -> str:
    """Neaten a string."""
    parts = str(raw).split('_')
    new_parts = []
    for part in parts:
        new_parts.append(part[0].upper() + part[1:])
    return ' '.join(new_parts)


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
        line = '`{code}`: {name}'.format(**unit)
        if 'alt_search' in unit:
            line += ' (`{alt_code}` | {alt_name})'.format(
                alt_code=unit['alt_code'],
                alt_name=neaten(unit['alt_search'])
            )
        lines.append(line)
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
        f'{neaten(field)}: {obj[field]}' for field in footer_fields
    ))
    ignore_fields = [
        *footer_fields, 'name', 'description', 'image', 'alt_code',
        'alt_search'
    ]
    for field in obj:
        if field not in ignore_fields:
            value = obj[field]
            if isinstance(value, list):
                parts = value or ['None']
            else:
                parts = [value]
            value = ', '.join(neaten(part) for part in parts)
            e.add_field(name=neaten(field), value=value)
    return e


@lru_cache(1024)
def lookup(object_type: str, search: str) -> typing.Optional[str]:
    """Lookup an object by user search."""
    data = load_data(object_type)
    search = search.lower().replace(' ', '').replace('-', '').replace("'", '')
    for full_name in data:
        codes = (data[full_name]['code'], data[full_name].get('alt_code'))
        if search in codes:
            return full_name
    possible = []
    for full_name in data:
        if search in full_name.replace('_', ''):
            possible.append(full_name)
        elif search in data[full_name].get('alt_search', '').replace('_', ''):
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
        }
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
            **type(self).embed_opts.get(self.object_type, {})
        )
