"""Model for a tag."""
from __future__ import annotations

from discord.ext import commands

import peewee

from .database import BaseModel, db


class NameFieldQuery:
    """Type for a name queries so we can recognise and avoid quoting them."""

    def __init__(self, value: str):
        """Store the value."""
        self.value = value


class NamesField(peewee.CharField):
    """A field for storing a list of tag names."""

    def db_value(self, names: list[str]) -> str:
        """Join the names together."""
        if isinstance(names, NameFieldQuery):
            return names.value
        return super().db_value('|' + '|'.join(names) + '|')

    def python_value(self, value: str) -> list[str]:
        """Split the names up."""
        return super().python_value(value).strip('|').split('|')

    def __eq__(self, rhs: str) -> peewee.Expression:
        """Make an expression to check if the names include some name."""
        return peewee.Expression(self, 'ILIKE', NameFieldQuery(f'%|{rhs}|%'))

    # __hash__ is not inherited if __eq__ is overwritten.
    __hash__ = peewee.CharField.__hash__


class Tag(BaseModel):
    """Model for a tag."""

    names = NamesField(max_length=1024)
    content = peewee.CharField(max_length=2000)
    uses = peewee.IntegerField(default=0)

    @classmethod
    async def convert(cls, ctx: commands.Context, raw_argument: str) -> Tag:
        """Convert a Discord.py argument to a tag."""
        tag = cls.get_or_none(cls.names == raw_argument)
        if not tag:
            raise commands.BadArgument(f'Tag `{raw_argument}` not found.')
        return tag

    def __str__(self) -> str:
        """Get the first name of this tag."""
        return self.names[0]


class TagQuery(BaseModel):
    """A question that was asked prior to a tag being used.

    Tracked for the possibility of automatic tags (!?!?).
    """

    tag = peewee.ForeignKeyField(Tag, on_delete='CASCADE')
    message = peewee.CharField(max_length=2000)


db.create_tables([Tag, TagQuery])
