from discord.ext.commands import (
    Context, BadArgument, MemberConverter, Converter
)
from discord.ext.commands.view import StringView
from tools.cache import cache, DONT_CACHE, BYPASS_CACHE
from tools import sheetsapi
import typing
import discord
from inspect import Parameter


def level_id(argument: str) -> int:
    """A converter for the game levels."""
    try:
        level = int(argument)
    except ValueError:
        raise BadArgument(f'No such level `{argument}`.')
    if level not in range(10):
        raise BadArgument(f'No such level `{level}`.')
    return level


def game_id(argument: str) -> typing.Tuple[int]:
    try:
        return sheetsapi.get_game_row(argument)
    except (IndexError, ValueError):
        raise BadArgument(f'Invalid game ID `{argument}`.')


class StaticPlayerConverter(MemberConverter):
    """Converter for player searches."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_only = True

    async def convert(self, ctx: Context, argument: str) -> sheetsapi.Player:
        """Convert a player search argument."""
        try:
            user = await super().convert(ctx, argument)
            searches = (user.name, user.display_name)
        except BadArgument:
            searches = (argument,)
        async with ctx.typing():
            possible = search_player(searches, self.static_only)
        if not possible:
            raise BadArgument(
                f'Could not find player `{argument}`. Try being less '
                'specific, or mentioning a user.'
            )
        elif len(possible) > 1:
            raise BadArgument(
                f'Found multiple players by search `{argument}`. Try being '
                'more specific, or mentioning a user.'
            )
        return possible[0]


class PlayerConverter(StaticPlayerConverter):
    """Converter for player searches where we need variable attributes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_only = False
        

@cache
def search_player(
        searches: typing.Tuple[str],
        static_only: bool = True,
        bypass_cache: bool = False,
        ) -> typing.List[sheetsapi.Player]:
    """Search for a player.

    This can be by discord user, or a search for discord name /
    polytopia name / friend code.
    """
    searches = tuple(search.lower() for search in searches)
    possible = []
    if static_only:
        if bypass_cache:
            # pylint: disable=too-many-function-args
            players = sheetsapi.get_players_static(BYPASS_CACHE)
        else:
            players = sheetsapi.get_players_static()
    else:
        players = sheetsapi.get_players()
    for player in players:
        fields = (
            player.discord_name, player.polytopia_name, player.friend_code
        )
        for field in fields:
            added = False
            for search in searches:
                if search in field.lower():
                    possible.append(player)
                    added = True
                    break
            if added:
                break
    if static_only:
        if (not bypass_cache) and (not possible):
            return search_player(searches, static_only, bypass_cache=True)
        else:
            return possible
    else:
        return possible, DONT_CACHE


class ManyConverter(Converter):
    """Converter for multiple lists of arguments."""

    def __init__(self, seperator='\n', **params):
        """Create the converter."""
        self.params = [
            Parameter(
                name, Parameter.POSITIONAL_ONLY, annotation=params[name]
            ) for name in params
        ]
        self.seperator = seperator

    async def convert(self, ctx: Context, argument: str):
        """Convert a list of lists of arguments."""
        lines = argument.strip(self.seperator).split(self.seperator)
        argument_sets = []
        for line in lines:
            view = StringView(line)
            argument_sets.append([])
            for param in self.params:
                converter = param.annotation
                arg = view.get_quoted_word()
                view.skip_ws()
                argument_sets[-1].append(
                    await ctx.command.do_conversion(
                        ctx, converter, arg, param
                    )
                )
        return argument_sets
