"""Model to record yellow/red timeouts of players."""
from __future__ import annotations

from datetime import datetime

from discord.ext import commands

import peewee

from .database import db, BaseModel
from .games import GamePlayer
from .players import Player


class Timeout(BaseModel):
    """Model to record yellow/red timeouts of players."""

    game_player = peewee.ForeignKeyField(
        GamePlayer, backref='timeouts', on_delete='CASCADE'
    )
    screenshot_url = peewee.CharField(max_length=2047)
    is_timeout = peewee.BooleanField()    # True=red, False=yellow
    reported_by = peewee.ForeignKeyField(Player, on_delete='SET NULL')
    reported_at = peewee.DateTimeField(default=datetime.now)

    @classmethod
    async def convert(
            cls, ctx: commands.Context, raw_argument: str) -> Timeout:
        """Convert a Discord.py argument to a game."""
        try:
            timeout_id = int(raw_argument)
        except ValueError:
            raise commands.BadArgument(f'Invalid timeout ID `{raw_argument}`.')
        timeout = Timeout.get_or_none(Timeout.id == timeout_id)
        if not timeout:
            raise commands.BadArgument(f'Timeout ID `{timeout_id}` not found.')
        return timeout

    @property
    def summary(self) -> str:
        """Get a line to summarise the timeout."""
        emoji = 'red_circle' if self.is_timeout else 'yellow_circle'
        line = f':{emoji}: <{self.screenshot_url}>'
        if self.reported_by:
            line += f' by **{self.reported_by.display_name}**'
        # Remove milliseconds.
        time = str(self.reported_at).split('.')[0]
        return line + f' at **{time}** (*ID: {self.id}*)'


db.create_tables([Timeout])
