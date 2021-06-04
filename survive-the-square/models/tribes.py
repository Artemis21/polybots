"""Tools for storing, displaying and parsing lists of tribes."""
from __future__ import annotations

import enum
import re
from typing import Iterable, Iterator, Union

from discord.ext import commands

import peewee


class Tribe(enum.Enum):
    """An enum for each in-game tribe."""

    AI_MO = enum.auto()
    XIN_XI = enum.auto()
    OUMAJI = enum.auto()
    BARDUR = enum.auto()
    VENGIR = enum.auto()
    ZEBASI = enum.auto()
    KICKOO = enum.auto()
    YADAKK = enum.auto()
    CYMANTI = enum.auto()
    ELYRION = enum.auto()
    POLARIS = enum.auto()
    LUXIDOOR = enum.auto()
    HOODRICK = enum.auto()
    QUETZALI = enum.auto()
    IMPERIUS = enum.auto()
    AQUARION = enum.auto()

    @classmethod
    async def convert(cls, ctx: commands.Context, raw_argument: str) -> Tribe:
        """Convert a Discord.py argument to a tribe."""
        for from_, to in zip('∑∫ỹȱŋă', 'elyrna'):
            raw_argument = raw_argument.replace(from_, to)
        argument = re.sub('[^A-Z]', '', raw_argument.upper())
        if not argument:
            raise commands.BadArgument(
                'Please use latin characters to specify a tribe.'
            )
        matches = []
        for tribe in cls:
            tribe_name = tribe.name.replace('_', '')
            if tribe_name.startswith(argument):
                matches.append(tribe)
        if len(matches) == 1:
            return matches[0]
        if matches:
            raise commands.BadArgument(
                f'Multiple tribes found matching `{raw_argument}`, try using '
                'more letters.'
            )
        raise commands.BadArgument(
            f'No tribe found matching `{raw_argument}`.'
        )

    def __str__(self) -> str:
        """Get the name of the tribe."""
        return self.name.lower().replace('_', '-')


class TribeList:
    """A list of tribes that allows updating with += and -=.

    Also acts as a Discord.py converter for a list of tribes. It is better
    than commands.Greedy for our use case because it errors if any tribe is
    invalid (but this also means no arguments can come after it).
    """

    @classmethod
    async def convert(
            cls, ctx: commands.Context, raw_argument: str) -> TribeList:
        """Convert a Discord.py argument to a TribeList."""
        tribes = []
        raw_tribes = raw_argument.split(' ')
        for raw_tribe in raw_tribes:
            if raw_tribe.lower() == 'all':
                return cls(Tribe)
            tribe = await Tribe.convert(ctx, raw_tribe)
            tribes.append(tribe)
        return cls(tribes)

    def __init__(self, tribes: tuple[Tribe]):
        """Store the list of tribes."""
        self.tribes = tuple(tribes)

    def __str__(self) -> str:
        """Represent the list as a human-readable string."""
        return ' '.join(tribe.emoji for tribe in self.tribes)

    def __iadd__(self, other: Union[Tribe, Iterable[Tribe]]) -> TribeList:
        """Add a tribe or tribes to the list."""
        if isinstance(other, Tribe):
            return TribeList((*self.tribes, other))
        else:
            return TribeList((*self.tribes, *other))

    def __isub__(self, other: Union[Tribe, Iterable[Tribe]]) -> TribeList:
        """Remove a tribe or tribes from the list."""
        if isinstance(other, Tribe):
            return TribeList(tuple(set(self.tribes) - {other}))
        else:
            return TribeList(tuple(set(self.tribes) - set(other)))

    def __iter__(self) -> Iterator[Tribe]:
        """Get the list of tribes, for iterating over."""
        for tribe in self.tribes:
            yield tribe
        return StopIteration


class TribeListField(peewee.Field):
    """A field to store a list of tribes."""

    field_type = 'smallint'    # 2 bytes

    def db_value(self, tribes: TribeList) -> int:
        """Convert a list of tribe enum instances to a series of bit flags."""
        value = 0
        for tribe in tribes:
            value |= 1 << tribe.value
        return value

    def python_value(self, value: int) -> TribeList:
        """Convert a series of bit flags to a list of tribe enum instances."""
        tribes = []
        for tribe in Tribe:
            if value & (1 << tribe.value):
                tribes.append(tribe)
        return TribeList(tribes)
