"""Peewee model for a player."""
from __future__ import annotations

from peewee import IntegerField, TextField

from . import timezones
from .database import db, BaseModel
from .tribes import Tribe, TribeList, TribeListField


class Player(BaseModel):
    """Model representing a player."""

    discord_id = IntegerField(primary_key=True)
    mobile_name = TextField(null=True)
    steam_name = TextField(null=True)
    utc_offset = timezones.TimezoneField(null=True)
    tribes = TribeListField(default=TribeList((
        Tribe.XIN_XI, Tribe.BARDUR, Tribe.OUMAJI, Tribe.IMPERIUS
    )))

    @classmethod
    def get_player(cls, discord_id: int) -> Player:
        """Get a player by discord ID, or create one if not found."""
        if player := cls.get_or_none(cls.discord_id == discord_id):
            return player
        return cls.create(discord_id=discord_id)


db.create_tables([Player])
