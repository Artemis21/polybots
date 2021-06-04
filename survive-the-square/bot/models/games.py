"""Models relating to games."""
from __future__ import annotations

import re
from collections import namedtuple
from typing import Optional

import discord
from discord.ext import commands

from peewee import fn, BooleanField, ForeignKeyField, IntegerField

from .database import db, BaseModel
from .players import Player


UserData = namedtuple('UserData', [
    'name', 'possesive', 'to_be', 'to_have', 'user'
])

NO_PERMS = discord.PermissionOverwrite(
    read_messages=False, send_messages=False
)
READ_PERMS = discord.PermissionOverwrite(
    read_messages=True, send_messages=False
)
WRITE_PERMS = discord.PermissionOverwrite(
    read_messages=True, send_messages=True
)


class Game(BaseModel):
    """Model representing a game."""

    is_steam = BooleanField(default=False)
    size = IntegerField(default=8)
    category_id = IntegerField(null=True)
    observer_channel_id = IntegerField(null=True)
    observer_role_id = IntegerField(null=True)
    player_channel_id = IntegerField(null=True)
    player_role_id = IntegerField(null=True)
    side_1_role_id = IntegerField(null=True)
    side_2_role_id = IntegerField(null=True)
    side_1_channel_id = IntegerField(null=True)
    side_2_channel_id = IntegerField(null=True)

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
    def space_count(self) -> int:
        """Get the number of spaces available in the game.

        Includes spaces that have already been taken.
        """
        return self.size * 2

    @property
    def member_count(self) -> int:
        """Count the members in the game."""
        return GameMember.select().where(GameMember.game == self).count()

    @property
    def player_list(self) -> str:
        """Get a human-readable list of players in the game."""
        lines = []
        for side in (1, 2):
            lines.append(f'**__Side {side}__**')
            players = Player.select().join(GameMember).where(
                GameMember.game == self,
                GameMember.side == side
            )
            for player in players:
                ign = (
                    player.steam_name if self.is_steam else player.mobile_name
                )
                lines.append(f'<@{player.discord_id}> - `{ign}`')
            if not players.count():
                lines.append('*No-one yet*')
        return '\n'.join(lines)

    async def new_role(self, guild: discord.Guild, name: str) -> discord.Role:
        """Make a Discord role for this game."""
        return await guild.create_role(
            name=f'{self.name} - {name}', mentionable=True
        )

    async def setup(self, guild: discord.Guild):
        """Setup the Discord roles and channels for this game."""
        observer_role = await self.new_role(guild, 'Observer')
        self.observer_role_id = observer_role.id
        player_role = await self.new_role(guild, 'Player')
        self.player_role_id = player_role.id
        side_1_role = await self.new_role(guild, 'Side 1')
        self.side_1_role_id = side_1_role.id
        side_2_role = await self.new_role(guild, 'Side 2')
        self.side_2_role_id = side_2_role.id
        category = await guild.create_category(name=self.name)
        self.category_id = category.id
        base_perms = {guild.default_role: NO_PERMS, observer_role: READ_PERMS}
        self.observer_channel_id = (await category.create_text_channel(
            name='audience',
            overwrites={
                **base_perms,
                observer_role: WRITE_PERMS, player_role: WRITE_PERMS
            }
        )).id
        self.player_channel_id = (await category.create_text_channel(
            name='diplomatic-relations',
            overwrites={**base_perms, player_role: WRITE_PERMS}
        )).id
        self.side_1_channel_id = (await category.create_text_channel(
            name='side-1', overwrites={**base_perms, side_1_role: WRITE_PERMS}
        )).id
        self.side_2_channel_id = (await category.create_text_channel(
            name='side-2', overwrites={**base_perms, side_2_role: WRITE_PERMS}
        )).id
        self.save()

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
            return UserData(
                name=user.display_name,
                possesive='their',
                to_be='is',
                to_have='has',
                user=user
            )
        else:
            return UserData(
                name='you',
                possesive='your',
                to_be='are',
                to_have='have',
                user=ctx.author
            )

    def player_can_join(
            self,
            ctx: commands.Context,
            user: UserData,
            player: Player) -> bool:
        """Check if a player can join this game (with logging)."""
        wrong_game_type = (
            f'Error: {self.name} is a {{0}} game, but {user.name} '
            f'{user.to_have} not set {user.possesive} {{0}} name. '
            f'Do `{ctx.prefix}{{0}}-name` to set it.'
        )
        if self.is_steam:
            if not player.steam_name:
                ctx.logger.log(wrong_game_type.format('steam'))
                return False
        else:
            if not player.mobile_name:
                ctx.logger.log(wrong_game_type.format('mobile'))
                return False
        if self.get_member(player):
            ctx.logger.log(
                f'Error: {user.name} {user.to_be} already in game {self.id}.'
            )
            return False
        return True

    async def add_player(
            self, ctx: commands.Context, user: discord.Member = None):
        """Add a player to the game."""
        user = self.user_info(ctx, user)
        player = Player.get_player(user.user.id)
        if not self.player_can_join(ctx, user, player):
            return
        side = GameMember.choose_side(self)
        side_channel = ctx.guild.get_channel(
            self.side_1_channel_id if side == 1 else self.side_2_channel_id
        )
        observer_role = ctx.guild.get_role(self.observer_role_id)
        player_role = ctx.guild.get_role(self.player_role_id)
        channel_id = (await side_channel.category.create_text_channel(
            user.user.display_name,
            position=side_channel.position,
            overwrites={
                ctx.guild.default_role: NO_PERMS,
                observer_role: READ_PERMS,
                player_role: NO_PERMS,
                user.user: WRITE_PERMS
            }
        )).id
        GameMember.create(
            player=player, game=self, side=side, channel_id=channel_id
        )
        side_role = ctx.guild.get_role(
            self.side_1_role_id if side == 1 else self.side_2_role_id
        )
        player_role = ctx.guild.get_role(self.player_role_id)
        await user.user.add_roles(player_role, side_role)
        ctx.logger.log(f'Added {user.name} to game {self.id}.')
        if self.member_count >= self.space_count:
            self.is_open = False
            self.save()
            ctx.logger.log(f'{self.name} is now full.')

    async def remove_player(
            self, ctx: commands.Context, user: discord.Member = None):
        """Remove a player from the game."""
        user = self.user_info(ctx, user)
        player = Player.get_player(user.user.id)
        if member := self.get_member(player):
            side_role = ctx.guild.get_role(
                self.side_1_role_id if member.side == 1
                else self.side_2_role_id
            )
            player_role = ctx.guild.get_role(self.player_role_id)
            await user.user.remove_roles(player_role, side_role)
            await ctx.guild.get_channel(member.channel_id).delete()
            member.delete_instance()
            ctx.logger.log(f'Removed {user.name} from game {self.id}.')
        else:
            ctx.logger.log(
                f'Error: {user.name} {user.to_be} not in game {self.id}.'
            )


class GameMember(BaseModel):
    """Many-to-many field between Game and Player."""

    game = ForeignKeyField(model=Game)
    player = ForeignKeyField(model=Player)
    channel_id = IntegerField()
    side = IntegerField()    # Either 1 or 2.

    @classmethod
    async def convert(
            cls, ctx: commands.Context, raw_argument: str) -> GameMember:
        """Get a member of the game this command was run for."""
        game = Game.get_or_none(Game.category_id == ctx.channel.category_id)
        if not game:
            raise commands.BadArgument(
                'This command must be run in a game channel.'
            )
        members = cls.select().where(cls.game_id == game.id)
        matches = []
        search = re.sub(r'[^a-z0-9]', '', raw_argument.lower())
        for member in members:
            if str(member.player_id) == search:
                return member
            if await member.name_matches(ctx.guild, search):
                matches.append(member)
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise commands.BadArgument(
                f'No game members found by search {search!r}.'
            )
        raise commands.BadArgument(
            f'Multiple game members found by search {search!r}.'
        )

    @classmethod
    def choose_side(cls, game: Game) -> int:
        """Choose the side of a game with fewer members."""
        side_1, side_2 = cls.select(
            fn.COUNT(cls.id).filter(cls.side == 1),
            fn.COUNT(cls.id).filter(cls.side == 2)
        ).where(cls.game == game).scalar(as_tuple=True)
        return 1 if side_1 <= side_2 else 2

    async def get_user(self, guild: discord.Guild) -> Optional[discord.Member]:
        """Get the Discord member for this game member."""
        if user := guild.get_member(self.player_id):
            return user
        try:
            return await guild.fetch_member(self.player_id)
        except discord.HTTPException:
            return None

    async def name_matches(self, guild: discord.Guild, search: str) -> bool:
        """Check if the player's name matches a given search."""
        user = await self.get_user(guild)
        if not user:
            return False
        names = [user.display_name, user.name]
        return any(
            search in re.sub(r'[^a-z0-9]', '', name.lower())
            for name in names
        )


db.create_tables([Game, GameMember])
