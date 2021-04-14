"""Tools for handling enums in database fields."""
from __future__ import annotations

import enum
import re
from typing import Any, Optional, Type

from discord.ext import commands

import peewee


class BaseEnum(enum.Enum):
    """Base class to provide utilities to enums."""

    @classmethod
    def search(cls, query: str) -> list[BaseEnum]:
        """Search for an option by name."""
        argument = re.sub('[^A-Z]', '', query.upper())
        matches = []
        for option in cls:
            if option.name.replace('_', '').startswith(argument):
                matches.append(option)
        return matches

    @classmethod
    async def convert(
            cls, ctx: commands.Context, raw_argument: str) -> BaseEnum:
        """Convert a Discord.py argument to an instance of this enum."""
        matches = cls.search(raw_argument)
        if len(matches) == 1:
            return matches[0]
        type_name = cls.__name__.lower()
        if matches:
            raise commands.BadArgument(
                f'Multiple {type_name}s found matching `{raw_argument}`, '
                f'try using more letters.'
            )
        raise commands.BadArgument(
            f'No {type_name} found matching `{raw_argument}`.'
        )

    def __str__(self) -> str:
        """Get a human-readable representation of the enum."""
        return self.name.title().replace('_', ' ')


class EnumField(peewee.SmallIntegerField):
    """A field where each value is an integer representing an option."""

    def __init__(
            self, options: Type[enum.Enum], **kwargs: Any):
        """Create a new enum field."""
        self.options = options
        super().__init__(**kwargs)

    def python_value(self, raw: int) -> Optional[enum.Enum]:
        """Convert a raw number to an enum value."""
        if raw is None:
            return None
        number = super().python_value(raw)
        return self.options(number)

    def db_value(self, instance: enum.Enum) -> Optional[int]:
        """Convert an enum value to a raw number."""
        if instance is None:
            return super().db_value(None)
        if not isinstance(instance, self.options):
            raise TypeError(f'Instance is not of enum class {self.options}.')
        number = instance.value
        return super().db_value(number)


class League(BaseEnum):
    """A Polychampions sub-league."""

    NOVA = 1
    JUNIOR = 2
    PRO = 3


class Team(BaseEnum):
    """A Polychampions team."""

    BOMBERS = 1
    VIKINGS = 2
    CRAWFISH = 3
    DRAGONS = 4
    REAPERS = 5
    JETS = 6
    LIGHTNING = 7
    MALLARDS = 8
    PLAGUE = 9
    RONIN = 10
    SPARKIES = 11
    WILDFIRE = 12
