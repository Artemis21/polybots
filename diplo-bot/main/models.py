"""Peewee ORM models."""
from __future__ import annotations

from collections import namedtuple

import discord
from discord.ext import commands

import peewee

from . import config, timezones
from .tribes import Tribe, TribeList, TribeListField


UserData = namedtuple('UserData', ['name', 'to_be', 'user'])

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
    mobile_name = peewee.TextField(null=True)
    steam_name = peewee.TextField(null=True)
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
    is_open = peewee.BooleanField(default=True)
    is_steam = peewee.BooleanField(default=False)
    limit = peewee.IntegerField(default=14)

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

    def user_info(
            self, ctx: commands.Context,
            user: discord.Member = None) -> UserData:
        """Get the name, ID and conjugation of 'to be' to refer to a user."""
        if user:
            return UserData(user.display_name, 'is', user)
        else:
            return UserData('you', 'are', ctx.author)

    async def add_player(
            self, ctx: commands.Context, user: discord.Member = None):
        """Add a player to the game."""
        user = self.user_info(ctx, user)
        player = Player.get_player(user.user.id)
        if self.is_steam:
            if not player.steam_name:
                ctx.logger.log(
                    f'Error: {self.name} is a steam game, but you have not '
                    f'set your steam name. Do `{ctx.prefix}steam-name` to '
                    'set it.'
                )
                return
        else:
            if not player.mobile_name:
                ctx.logger.log(
                    f'Error {self.name} is a mobile game, but you have not '
                    f'set your steam name. Do `{ctx.prefix}mobile-name` to '
                    'set it.'
                )
                return
        if self.get_member(player):
            ctx.logger.log(
                f'Error: {user.name} {user.to_be} already in game {self.id}.'
            )
        else:
            GameMember.create(player=player, game=self)
            role = ctx.guild.get_role(self.role_id)
            await user.user.add_roles(role)
            ctx.logger.log(f'Added {user.name} to game {self.id}.')
            if self.member_count >= self.limit:
                self.is_open = False
                self.save()
                ctx.logger.log(f'{self.name} full. Game closed.')

    async def remove_player(
            self, ctx: commands.Context, user: discord.Member = None):
        """Remove a player from the game."""
        user = self.user_info(ctx, user)
        player = Player.get_player(user.user.id)
        if member := self.get_member(player):
            member.delete_instance()
            role = ctx.guild.get_role(self.role_id)
            await user.user.remove_roles(role)
            ctx.logger.log(f'Removed {user.name} from game {self.id}.')
        else:
            ctx.logger.log(
                f'Error: {user.name} {user.to_be} not in game {self.id}.'
            )


class GameMember(BaseModel):
    """Many-to-many field between Game and Player."""

    game = peewee.ForeignKeyField(model=Game)
    player = peewee.ForeignKeyField(model=Player)


MODELS = [Player, Game, GameMember]

db.create_tables(MODELS)
