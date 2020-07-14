"""Unit stats."""
from functools import lru_cache
import json
import typing

import discord
from discord.ext import commands


@lru_cache(1)
def load_data() -> typing.Dict:
    """Load data from the file."""
    with open('data/units.json') as f:
        return json.load(f)


@lru_cache(1)
def list_all() -> str:
    """List all units."""
    lines = []
    for unit in load_data().values():
        lines.append('`{short}`: {name}'.format(**unit))
    return '\n'.join(lines)


@lru_cache(32)
def embed(unit_name: str) -> discord.Embed:
    """Create an embed to display unit information."""
    unit = load_data()[unit_name]
    return discord.Embed(
        title=unit['name'], description=unit['about']
    ).add_field(
        name='Skills',
        value=', '.join(skill.title() for skill in unit['skills']) or 'None',
        inline=False
    ).add_field(
        name='Health', value=unit['health']
    ).add_field(
        name='Attack', value=unit['attack']
    ).add_field(
        name='Movement', value=unit['movement']
    ).add_field(
        name='Cost', value=unit['cost']
    ).add_field(
        name='Defence', value=unit['defence']
    ).add_field(
        name='Range', value=unit['range']
    ).set_thumbnail(url=unit['image']).set_footer(
        text=f"Tech required: {unit['tech'].title()}"
    )


@lru_cache(256)
def lookup(search: str) -> typing.Optional[str]:
    """Lookup a unit by user search."""
    data = load_data()
    search = search.lower().replace(' ', '_').replace('-', '_')
    for full_name in data:
        if search == data[full_name]['short']:
            return full_name
    possible = []
    for full_name in data:
        if search in full_name:
            possible.append(full_name)
    if len(possible) == 1:
        return possible[0]
    elif possible:
        raise commands.BadArgument(
            f'Multiple units found by search "{search}". '
            'Try being more specific, or use a unit code.'
        )
    else:
        raise commands.BadArgument(
            f'Could not find any units by search "{search}". '
            'Try being less specific, or use a unit code.'
        )
