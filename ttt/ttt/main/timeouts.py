"""Tools for managing timeouts."""
from discord.ext import commands

from ..models import Game, Player, Timeout


def report_timeout(
        ctx: commands.Context,
        game: Game,
        player: Player,
        is_timeout: bool) -> str:
    """Report a red/yellow timeout from a command."""
    if not game.get_member(ctx.ttt_player):
        return 'You are not in this game.'
    if not (game_player := game.get_member(player)):
        return f'{game_player.display_name} is not in this game.'
    if len(ctx.message.attachments) != 1:
        return 'Please attach exactly one screenshot to prove this.'
    Timeout.create(
        game_player=game_player,
        screenshot_url=ctx.message.attachments[0].url,
        is_timeout=is_timeout,
        reported_by=ctx.ttt_player
    )
    return f'Reported timeout ({game.mention_all()}).'
