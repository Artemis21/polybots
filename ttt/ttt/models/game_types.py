"""Field for storing a game type by ID."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from discord.ext import commands

import peewee

from .tribes import Tribe
from ..main.config import TT_GAME_TYPES


@dataclass
class GameType:
    """One of the game types."""

    id: int
    map_type: str
    tribe: Tribe
    alternative_tribe: Tribe

    @classmethod
    def from_id(cls, game_type_id: int) -> Optional[GameType]:
        """Get a game type by ID."""
        try:
            data = TT_GAME_TYPES[game_type_id]
        except IndexError:
            return None
        return cls(
            id=game_type_id,
            map_type=data['map'],
            tribe=Tribe.search(data['tribe'])[0],
            alternative_tribe=Tribe.search(data['alt_tribe'])[0]
        )

    @classmethod
    async def convert(
            cls, ctx: commands.Context, raw_argument: str) -> GameType:
        """Convert a Discord.py argument to a game type, by ID."""
        try:
            game_type_id = int(raw_argument)
        except ValueError:
            raise commands.BadArgument(
                f'Invalid game type ID `{raw_argument}` (must be a number).'
            )
        if game_type := cls.from_id(game_type_id):
            return game_type
        raise commands.BadArgument(
            f'No game type found by ID `{raw_argument}`.'
        )

    def __str__(self) -> str:
        """Display the game type in a human-readable format."""
        return (
            f'**Map type:** {self.map_type} (tiny)\n'
            f'**Tribe:** {self.tribe}\n'
            f'*If not all players have {self.tribe}, everyone must '
            f'use {self.alternative_tribe}.*'
        )


class GameTypeField(peewee.Field):
    """Database field that stores a game type by ID."""

    field_type = 'smallint'

    def db_value(self, game_type: GameType) -> Optional[int]:
        """Store a game type as its ID."""
        if game_type is None:
            return
        return game_type.id

    def python_value(self, value: int) -> Optional[GameType]:
        """Load a game type from its ID."""
        if value is None:
            return
        return GameType.from_id(value)
