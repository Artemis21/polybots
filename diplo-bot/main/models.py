"""Peewee ORM models."""
from __future__ import annotations

import peewee

from . import config


db = peewee.SqliteDatabase(str(config.BASE_PATH / 'db.sqlite3'))


class BaseModel(peewee.Model):
    """Base model to set default settings."""

    class Meta:
        """Peewee settings."""

        database = db
        use_legacy_table_names = False


class Player(BaseModel):
    """Model representing a player."""

    discord_id = peewee.IntegerField(primary_key=True)
    wins = peewee.IntegerField(default=0)

    @classmethod
    def get_player(cls, discord_id: int) -> Player:
        """Get a player by discord ID, or create one if not found."""
        if player := cls.get_or_none(cls.discord_id == discord_id):
            return player
        return cls.create(discord_id=discord_id)

    @classmethod
    def give_many_wins(cls, discord_ids: list[int]):
        """Award a win to multiple players."""
        for discord_id in discord_ids:
            player = cls.get_player(discord_id)
            player.wins += 1
            player.save()

    @classmethod
    def get_leaderboard(cls) -> list[tuple[int, int]]:
        """Get the leaderboard.

        Returns a list of tuples, each tuple is (discord_id, wins).
        """
        query = cls.select().where(cls.wins != 0).order_by(-cls.wins).limit(10)
        lb = []
        for player in query:
            lb.append((player.discord_id, player.wins))
        return lb


MODELS = [Player]

db.create_tables(MODELS)
