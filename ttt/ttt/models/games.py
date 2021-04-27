"""The game model."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional

import discord
from discord.ext import commands

import peewee
from peewee import fn

from .database import BaseModel, db
from .game_types import GameType, GameTypeField
from .players import Player
from .tribes import Tribe
from ..main import config, elo_api


def tribe_to_play(players: list[Player], game_type: GameType) -> Tribe:
    """Get the tribe a list of players should play for a game type."""
    for player in players:
        if game_type.tribe not in player.tribes:
            # Alternative tribe is always free, so everyone has it.
            return game_type.alternative_tribe
    return game_type.tribe


def first_type_not_played(players: list[Player]) -> Optional[GameType]:
    """Get the first game type none of a set of players have played."""
    player_ids = [player.discord_id for player in players]
    games = Game.select().join(GamePlayer).where(
        GamePlayer.player_id.in_(player_ids)
    )
    game_types_played = [game.game_type.id for game in games]
    type_id = 0
    while type_id in game_types_played:
        type_id += 1
    return GameType.from_id(type_id)


class Game(BaseModel):
    """One of the games in the tournament."""

    elo_bot_id = peewee.IntegerField(primary_key=True)
    game_type = GameTypeField()
    recheck_at = peewee.DateTimeField(null=True)
    # These can be discovered from the ELO bot API, we just store them in
    # the database to cache.
    game_name = peewee.CharField(max_length=255, null=True)
    won_at = peewee.DateTimeField(null=True)

    @classmethod
    async def recheck_games(cls):
        """Check any games due for rechecking."""
        now = datetime.now()
        games = cls.select().where(cls.recheck_at >= now)
        for game in games:
            await game.reload_from_elo_api()
        cls.update(recheck_at=None).where(cls.recheck_at >= now)

    @classmethod
    async def convert(cls, ctx: commands.Context, raw_argument: str) -> Game:
        """Convert a Discord.py argument to a game."""
        try:
            game_id = int(raw_argument)
        except ValueError:
            raise commands.BadArgument(f'Invalid game ID `{raw_argument}`.')
        game = Game.get_or_none(Game.elo_bot_id == game_id)
        if not game:
            raise commands.BadArgument(f'Game ID `{game_id}` not found.')
        return game

    @classmethod
    async def create_game(
            cls, players: list[Player], guild: discord.Guild) -> Game:
        """Create a game for the tourney (including on ELO bot).

        Exactly four users should be specified.
        """
        game_type = first_type_not_played(players)
        sides = [[player.discord_id] for player in players]
        name = f'TTT Friend Request {players[0].in_game_name}'
        tribe = tribe_to_play(players, game_type)
        notes = (
            f'Tiny Tourney 2\n'
            f'Map type: {game_type.map_type} (tiny)\n'
            f'Tribe: {tribe}'
        )
        game_id = await elo_api.new_game(elo_api.NewEloGame(
            game_name=name, notes=notes,
            guild_id=config.BOT_GUILD_ID,
            sides_discord_ids=sides,
            is_ranked=True, is_mobile=True
        ))
        game = cls.create(elo_bot_id=game_id, game_type=game_type)
        for position, player in enumerate(players):
            GamePlayer.create(game=game, player=player, position=position)
        await game.reload_from_elo_api()
        await game.send_notifications(guild)
        return game

    async def send_notifications(self, guild: discord.Guild):
        """Send members DMs to notify them of the game."""
        embed = self.embed()
        players = self.players
        members = '`, `'.join(
            (player.in_game_name or 'Unkown') for player in players[1:]
        )
        host = players[0].in_game_name
        for n, player in enumerate(players):
            if n == 0:
                message = (
                    'You have a new game to host. In game names (in order): '
                    f'`{members}`'
                )
            else:
                message = (
                    'You have been added to a game - please send a friend '
                    f'request to `{host}`'
                )
            user = (
                guild.get_member(player.discord_id)
                or await guild.fetch_member(player.discord_id)
            )
            try:
                dm = await user.create_dm()
                await dm.send(message, embed=embed)
            except discord.HTTPException:
                continue

    def check_winner(self, game_data: elo_api.EloGame):
        """Check the winner of the game is up to date with the ELO bot."""
        if not game_data.winner:
            GamePlayer.update(won=False).where(
                GamePlayer.game == self
            ).execute()
            return
        if not game_data.is_confirmed:
            return
        winner_id = None
        for side in game_data.sides:
            if side.id == game_data.winner:
                # Sides should only have one member.
                winner_id = side.members[0]
                break
        winner = GamePlayer.get_or_none(
            GamePlayer.player_id == winner_id, GamePlayer.game == self
        )
        if winner.won:
            # Win has already been processed.
            return
        winner.lost = False
        winner.won = True
        winner.ended_at = game_data.win_claimed_at
        winner.save()
        GamePlayer.update(
            won=False,
            lost=True,
            ended_at=fn.COALESCE(
                GamePlayer.ended_at, game_data.win_claimed_at)
        ).where(
            GamePlayer.game == self,
            GamePlayer.player_id != winner_id
        ).execute()

    async def reload_from_elo_api(self):
        """Reload the game from the ELO bot API."""
        game_data = await elo_api.get_game(self.elo_bot_id)
        self.check_winner(game_data)
        self.game_name = game_data.name
        self.save()

    @property
    def completed(self) -> bool:
        """Check if the game is completed."""
        return self.won_at is not None

    @property
    def players(self) -> Iterable[Player]:
        """Get the players in the game."""
        return Player.select().join(GamePlayer).where(
            GamePlayer.game == self
        ).order_by(GamePlayer.position)

    @property
    def tribe(self) -> Tribe:
        """Get the tribe that players should play."""
        return tribe_to_play(self.players, self.game_type)

    def get_member(self, player: Player) -> Optional[GamePlayer]:
        """Get a member of the game."""
        return GamePlayer.get_or_none(
            GamePlayer.game == self, GamePlayer.player == player
        )

    def embed(self) -> discord.Embed:
        """Get a summary of the game as a Discord embed."""
        roster = []
        members = GamePlayer.select().where(
            GamePlayer.game == self
        ).order_by(GamePlayer.position).join(Player)
        for member in members:
            name = f'**{member.player.display_name}**'
            if member.lost:
                name += ' :skull:'
            if member.won:
                name += ' :crown:'
            roster.append(name)
        description = ' vs '.join(roster) + '\n\n' + (
            f'**Map Type:** {self.game_type.map_type}\n'
            f'**Tribe:** {self.tribe}'
        )
        return discord.Embed(
            colour=config.COL_ACCENT,
            title=self.game_name,
            description=description
        ).set_author(name='Tiny Tourney 2').set_footer(
            text=f'$game {self.elo_bot_id} for more info.'
        )


class GamePlayer(BaseModel):
    """Many-to-many field between games and players."""

    game = peewee.ForeignKeyField(Game, backref='members', on_delete='CASCADE')
    player = peewee.ForeignKeyField(Player, on_delete='CASCADE')
    position = peewee.SmallIntegerField()
    won = peewee.BooleanField(default=False)
    lost = peewee.BooleanField(default=False)
    ended_at = peewee.DateTimeField(null=True)


db.create_tables([Game, GamePlayer])
