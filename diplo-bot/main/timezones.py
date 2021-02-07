"""Tool for parsing, displaying and storing timezones."""
from __future__ import annotations

import datetime
import re

from discord.ext import commands

import peewee


class Timezone:
    """Type to store a timezone and display it in various ways."""

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> Timezone:
        """Parse a Discord.py argument as a UTC offset."""
        argument = argument.upper()
        if argument in ('GMT', 'UTC'):
            return cls(False, 0, 0)
        argument = argument.removeprefix('UTC').removeprefix(
            'GMT'
        ).removeprefix('+')
        negative = argument.startswith('-')
        argument = argument.removeprefix('-')
        if re.match('[0-9]+$', argument):
            hours = int(argument)
            minutes = 0
        elif match := re.match('([0-9]+):([0-5][0-9])$', argument):
            hours = int(match.group(1))
            minutes = int(match.group(2))
        elif match := re.match(r'([0-9]+)\.([0-9]+)$', argument):
            hours = int(match.group(1))
            minutes = round(float('0.' + match.group(2)) * 60)
        else:
            raise commands.BadArgument('Unrecognised timezone format.')
        if hours > 24:
            raise commands.BadArgument('Offset more than UTC+24.')
        if hours < -24:
            raise commands.BadArgument('Offset less than UTC-24.')
        if minutes % 15:
            raise commands.BadArgument(
                'Offset minute part must be a multiple of 15 minutes.'
            )
        return cls(negative, hours, minutes)

    def __init__(self, negative: bool, hours: int, minutes: int):
        """Store the values that make up the UTC offset."""
        self.negative = negative
        self.hours = hours
        self.minutes = minutes

    def __str__(self) -> str:
        """Display the offset in a human-readable format."""
        sign = '-' if self.negative else '+'
        return f'UTC{sign}{self.hours}:{self.minutes:>02}'

    @property
    def timedelta(self) -> datetime.timedelta:
        """Get the offset as a timedelta, for easy comparison."""
        factor = -1 if self.negative else 1
        return datetime.timedelta(
            hours=factor * self.hours, minutes=factor * self.minutes
        )


class TimezoneField(peewee.Field):
    """Database field that stores a timezone (UTC offset).

    Stores offsets as an SQLite tinyint (1 byte) as follows (most to least
    significant bits):
    0      - Always a low bit.
    1      - Low if the offset is below zero, high otherwise.
    2 to 5 - The whole hour offset (a 4 bit integer).
    6      - If high, add 30 minutes to the offset.
    7      - If high, add 15 minutes to the offset.
    """

    field_type = 'tinyint'    # 1 byte

    def db_value(self, timezone: Timezone) -> int:
        """Convert a timezone to a 7 bit number."""
        if timezone is None:
            return
        value = 0
        if timezone.negative:
            value |= 1 << 7
        value |= timezone.hours << 2
        value |= timezone.minutes // 15
        return value

    def python_value(self, value: int) -> Timezone:
        """Convert a 7 bit number to a timezone."""
        if value is None:
            return
        negative = bool(value & (1 << 7))
        hours = (value & 0b111100) >> 2
        minutes = 15 * (value & 0b11)
        return Timezone(negative, hours, minutes)
