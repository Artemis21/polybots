"""The player model."""
from __future__ import annotations

from typing import Iterable, Optional

import discord
from discord.ext import commands
from discord.ext.commands.converter import MemberConverter

import peewee
from peewee import JOIN, fn

from .database import BaseModel, db
from .enums import EnumField, League, Team
from .timezones import Timezone, TimezoneField
from .tribes import Tribe, TribeList, TribeListField
from ..main import config, elo_api


class Player(BaseModel):
    """A player in the tournament."""

    discord_id = peewee.BigIntegerField(primary_key=True)
    tribes = TribeListField(default=TribeList((
        Tribe.XIN_XI, Tribe.BARDUR, Tribe.OUMAJI, Tribe.IMPERIUS
    )))
    # These can be discovered from the Discord API, we just store them
    # in the database to cache.
    display_name = peewee.CharField(max_length=255, null=True)
    avatar_url = peewee.CharField(max_length=2047, null=True)
    team = EnumField(Team, null=True)
    league = EnumField(League, null=True)
    # These can be discovered from the ELO bot API, we just store them in
    # the database to cache.
    timezone = TimezoneField(null=True)
    in_game_name = peewee.CharField(max_length=255, null=True)

    @classmethod
    async def convert(
            cls, ctx: commands.Context, raw_argument: str) -> Player:
        """Convert a Discord.py argument to a player, via a member."""
        # Allow errors to be raised by member converter.
        member = await MemberConverter().convert(ctx, raw_argument)
        player = cls.get_or_none(cls.discord_id == member.id)
        if not player:
            raise commands.BadArgument(
                f'{member.display_name} is not registerd.'
            )
        if member.guild.id == config.BOT_GUILD_ID:
            player.reload_from_discord_member(member)
        return player

    @classmethod
    def leaderboard(self) -> Iterable[Player]:
        """Get a leaderboard of all players."""
        return Player.select(
            Player,
            fn.COUNT(games.GamePlayer.id).filter(
                games.GamePlayer.won).alias('wins'),
            fn.COUNT(games.GamePlayer.id).filter(
                games.GamePlayer.lost).alias('losses'),
            fn.COUNT(games.GamePlayer.id).alias('total'),
            fn.COUNT(games.GamePlayer.id).filter(
                games.GamePlayer.won | games.GamePlayer.lost
            ).alias('complete')
        ).join(games.GamePlayer, JOIN.LEFT_OUTER).order_by(
            -fn.COUNT(games.GamePlayer.id),
            -fn.COUNT(games.GamePlayer.id).filter(
                games.GamePlayer.won | games.GamePlayer.lost),
            fn.COUNT(games.GamePlayer.id).filter(
                (~games.GamePlayer.won) & (~games.GamePlayer.lost))
        ).group_by(Player)

    async def reload_elo_data(self):
        """Reload data from the ELO bot API."""
        user_data = await elo_api.get_user(self.discord_id)
        self.in_game_name = user_data.mobile_name
        if user_data.utc_offset is not None:
            self.timezone = Timezone.from_hours(user_data.utc_offset)
        if team_data := user_data.teams.get(config.ELO_GUILD_ID):
            if team_data.hidden:
                self.league = League.NOVA
                self.team = None
            else:
                if team_data.pro:
                    self.league = League.PRO
                else:
                    self.league = League.JUNIOR
                self.team = Team.search(team_data.name.lower().strip('the '))[0]
        else:
            self.league = None
            self.team = None
        self.save()

    def reload_from_discord_member(self, member: discord.Member):
        """Reload data from a pre-fetched Discord member."""
        self.display_name = member.display_name
        self.avatar_url = str(member.avatar_url)
        self.save()

    async def reload_discord_data(self, client: discord.Client):
        """Reload data from the Discord API."""
        guild = client.get_guild(config.BOT_GUILD_ID)
        member = guild.get_member(self.discord_id)
        if not member:
            try:
                member = await guild.fetch_member(self.discord_id)
            except discord.HTTPException:
                return
        self.reload_from_discord_member(member)

    def embed(self) -> discord.Embed:
        """Give a human-readable player summary as a Discord embed."""
        description = (
            '**Timezone:** {0}\n**In-game name:** {1}\n**Tribes:**\n{2}'
        ).format(
            str(self.timezone) if self.timezone else 'Unknown',
            self.in_game_name or 'Unknown', str(self.tribes)
        )
        members = list(
            games.GamePlayer.select().where(
                games.GamePlayer.player == self
            ).join(games.Game)
        )
        wins = sum(1 for member in members if member.won)
        losses = sum(1 for member in members if member.lost)
        completed = wins + losses
        incomplete = len(members) - completed
        if self.team:
            team = f'{self.team} ({self.league})'
        else:
            team = str(self.league) if self.league else 'Unknown'
        return discord.Embed(
            title=self.display_name, description=description,
            colour=config.COL_ACCENT
        ).set_thumbnail(url=self.avatar_url).add_field(
            name='W/L/I',
            value=f'{wins}/{losses}/{incomplete}'
        ).add_field(name='Team', value=team).add_field(
            name='Games', value=self.game_list(members), inline=False)

    def game_list(
            self, members: Optional[list[games.GamePlayer]] = None) -> str:
        """Get a human readable list of the games the player is in."""
        if not members:
            members = games.GamePlayer.select().where(
                games.GamePlayer.player == self).join(games.Game)
        lines = ['**`    ID` State**']
        for member in members:
            if member.won:
                state = 'Won'
            elif member.lost:
                state = 'Lost'
            else:
                state = 'Ongoing'
            game = member.game
            lines.append(f'`{game.elo_bot_id:>6}` {state}')
        return '\n'.join(lines)


# Import after defining Player to avoid circular import problems.
from . import games    # noqa:E402,I100,I202


db.create_tables([Player])
