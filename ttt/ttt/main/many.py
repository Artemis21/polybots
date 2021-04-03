"""A Discord.py generic converter for converting repeated args.

It differs from commands.Greedy in that it errors if any argument is invalid,
instead of just treating that as the end of the list (but this also means no
arguments can come after it).
"""
import inspect
from typing import Any

from discord.ext import commands


class ManyConverter(commands.Converter):
    """A Discord.py generic converter for converting repeated args."""

    def __init__(self, item_converter: commands.Converter):
        """Store the converter."""
        self.item_converter = item_converter

    async def convert(
            self, ctx: commands.Context, raw_argument: str) -> list[Any]:
        """Convert a list of arguments."""
        param = inspect.Parameter('items', inspect.Parameter.VAR_POSITIONAL)
        items = []
        while raw_argument:
            raw_argument = raw_argument.strip()
            if raw_argument.startswith('"'):
                raw_argument = raw_argument[1:]
                try:
                    this_argument_ends = raw_argument.index('"')
                except ValueError:
                    raise commands.BadArgument('Unmatched quotes.')
            else:
                try:
                    this_argument_ends = raw_argument.index(' ')
                except ValueError:
                    this_argument_ends = len(raw_argument)
                this_argument = raw_argument
            this_argument = raw_argument[:this_argument_ends]
            raw_argument = raw_argument[this_argument_ends + 1:]
            items.append(await ctx.command.do_conversion(
                ctx, self.item_converter, this_argument, param
            ))
        return items


class _Many:
    """Type for creating ManyConverters."""

    def __getitem__(
            self, item_converter: commands.Converter) -> ManyConverter:
        """Get a many converter for a type."""
        return ManyConverter(item_converter)


Many = _Many()
