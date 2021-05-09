"""Tools for managing timeouts."""
import peewee

import discord
from discord.ext import commands

from ..models import Game, GamePlayer, Player, Timeout


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


def get_timeouts(game: Game) -> discord.Embed:
    """Get a list of timeouts for a game as an embed."""
    Reporter = Player.alias('reporter')
    return GamePlayer.select().where(GamePlayer.game == game).join(
        Timeout,
        peewee.JOIN.LEFT_OUTER,
        on=Timeout.game_player == GamePlayer.id
    ).join(
        Reporter,
        peewee.JOIN.LEFT_OUTER,
        on=Timeout.reported_by == Reporter.discord_id
    ).join(
        Player,
        on=GamePlayer.player == Player.discord_id
    ).group_by(GamePlayer.id)


def display_timeouts(game: Game) -> discord.Embed:
    """Display a list of timeouts-per-player."""
    players = get_timeouts(game)
    embed = discord.Embed(title=f'Timeouts for {game.game_name}').set_footer(
        text=f'ID: {game.elo_bot_id}'
    )
    for player in players:
        lines = []
        for timeout in player.timeouts:
            emoji = 'red_circle' if timeout.is_timeout else 'yellow_circle'
            line = f':{emoji}: <{timeout.screenshot_url}>'
            if timeout.reported_by:
                line += f' by **{timeout.reported_by.display_name}**'
            # Remove milliseconds.
            time = str(timeout.reported_at).split('.')[0]
            line += f' at **{time}**'
            lines.append(line)
        embed.add_field(
            name=player.player.display_name,
            value='\n'.join(lines) or '*No timeouts yet!*',
            inline=False
        )
    return embed
