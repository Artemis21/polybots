"""Peewee ORM models."""
from __future__ import annotations

from discord.ext import commands

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


class Game(BaseModel):
    """Model representing a game."""

    role_id = peewee.IntegerField(null=True)
    category_id = peewee.IntegerField(null=True)
    open = peewee.BooleanField(default=True)

    @classmethod
    async def convert(cls, ctx: commands.Context, raw_argument: str) -> Game:
        """Convert a Discord.py argument to a game."""
        try:
            game_id = int(raw_argument)
        except ValueError:
            raise commands.BadArgument(
                f'Invalid game ID `{raw_argument}` (not a number).'
            )
        game = cls.get_or_none(cls.id == game_id)
        if not game:
            raise commands.BadArgument(f'Game {game_id} not found.')
        return game

    @property
    def name(self) -> str:
        """Get the game's displayable name."""
        return f'Game {self.id}'

    @property
    def member_count(self) -> int:
        """Count the members in the game."""
        return GameMember.select().where(GameMember.game == self).count()

    def get_member(self, player: Player) -> GameMember:
        """Get the GameMember record associated with this game and a player."""
        return GameMember.get_or_none(
            GameMember.game == self,
            GameMember.player == player
        )


class GameMember(BaseModel):
    """Many-to-many field between Game and Player."""

    game = peewee.ForeignKeyField(model=Game)
    player = peewee.ForeignKeyField(model=Player)


MODELS = [Player, Game, GameMember]

db.create_tables(MODELS)
