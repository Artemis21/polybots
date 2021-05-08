"""Model to record yellow/red timeouts of players."""
from datetime import datetime

import peewee

from .database import db, BaseModel
from .games import GamePlayer
from .players import Player


class Timeout(BaseModel):
    """Model to record yellow/red timeouts of players."""

    game_player = peewee.ForeignKeyField(GamePlayer)
    screenshot_url = peewee.CharField(max_length=2047)
    is_timeout = peewee.BooleanField()    # True=red, False=yellow
    reported_by = peewee.ForeignKeyField(Player)
    reported_at = peewee.DateTimeField(default=datetime.now)


db.create_tables([Timeout])
