"""Tools for storing, displaying and parsing lists of tribes."""
from __future__ import annotations

from typing import Iterable, Iterator, Union

from discord.ext import commands

import peewee

from . import enums


class Tribe(enums.BaseEnum):
    """An enum for each in-game tribe."""

    XIN_XI = 1
    IMPERIUS = 2
    OUMAJI = 3
    BARDUR = 4
    KICKOO = 5
    LUXIDOOR = 6
    VENGIR = 7
    HOODRICK = 8
    ZEBASI = 9
    AI_MO = 10
    QUETZALI = 11
    YADAKK = 12
    AQUARION = 13
    ELYRION = 14
    POLARIS = 15
    CYMANTI = 16

    def __str__(self) -> str:
        """Get a human-readable representation of the enum."""
        return super().__str__().replace(' ', '-')


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

    def __init__(self, tribes: Iterable[Tribe]):
        """Store the list of tribes."""
        self.tribes = tuple(tribes)

    def __str__(self) -> str:
        """Represent the list as a human-readable string."""
        return ', '.join(map(str, self.tribes))

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

    field_type = 'integer'

    def db_value(self, tribes: TribeList) -> int:
        """Convert a list of tribe enum instances to a series of bit flags."""
        value = 0
        for tribe in tribes:
            value |= 1 << tribe.value
        return value

    def python_value(self, value: int) -> TribeList:
        """Convert a series of bit flags to a list of tribe enum instances."""
        tribes: list[Tribe] = []
        for tribe in Tribe:
            if value & (1 << tribe.value):
                tribes.append(tribe)
        return TribeList(tribes)
