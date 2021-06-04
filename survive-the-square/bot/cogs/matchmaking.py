"""Commands for creating and viewing games."""
import discord
from discord.ext import commands

from ..main import checks
from .. import models


class Matchmaking(commands.Cog):
    """Commands for creating and viewing games."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot

    @commands.command(
        brief='Create a game.', name='new-game', aliases=['ng', 'new']
    )
    @checks.admin
    async def new_game(
            self, ctx: commands.Context, platform: str, size: int = 8):
        """Create a new game, with an optional team size (default 8).

        Examples:
        `{{pre}}new-game steam 6`
        `{{pre}}new-game mobile`
        """
        if 'steam'.startswith(platform.lower()):
            is_steam = True
        elif 'mobile'.startswith(platform.lower()):
            is_steam = False
        else:
            await ctx.send(
                f'`{platform}` is not a recognised platform - use `steam` '
                'or `mobile`.'
            )
            return
        async with ctx.typing():
            game = models.Game.create(size=size, is_steam=is_steam)
            await game.setup(ctx.guild)
        await ctx.send(f'Created game {game.id}.')

    @commands.command(
        brief='Join a game.', name='join-game', aliases=['j', 'join']
    )
    async def join_game(self, ctx: commands.Context, game: models.Game):
        """Join a game by its ID.

        Example: `{{pre}}join 30`
        """
        if game.member_count < game.space_count:
            await game.add_player(ctx)
        else:
            await ctx.send(f'{game.name} is already full, sorry.')

    @commands.command(
        brief='Leave a game.', name='leave-game', aliases=['l', 'leave']
    )
    async def leave_game(self, ctx: commands.Context, game: models.Game):
        """Leave a game you are in.

        Example: `{{pre}}leave 45`
        """
        if game.member_count < game.space_count:
            await game.remove_player(ctx)
        else:
            await ctx.send(
                f'{game.name} is closed. Contact an admin to remove you.'
            )

    @commands.command(
        brief='Add a user to a game.', name='add-member', aliases=['a', 'add']
    )
    @checks.admin
    async def add_member(
            self, ctx: commands.Context, user: discord.Member,
            game: models.Game):
        """Manually add a user to a game.

        Example: `{{pre}}add @Artemis 35`
        """
        if game.member_count < game.space_count:
            await game.add_player(ctx, user)
        else:
            await ctx.send(f'{game.name} is already full.')

    @commands.command(
        brief='Remove a user from a game.', name='remove-member',
        aliases=['r', 'remove']
    )
    @checks.admin
    async def remove_member(
            self, ctx: commands.Context, user: discord.Member,
            game: models.Game):
        """Manually remove a user from a game.

        Example: `{{pre}}remove @Artemis 31`
        """
        if game.member_count >= game.space_count:
            ctx.logger.log(f'Warning: {game.name} is full.')
        await game.remove_player(ctx, user)

    @commands.command(brief='View a game.', aliases=['g'])
    async def game(self, ctx: commands.Context, game: models.Game = None):
        """View information on a game.

        Defaults to the game category you use the command in, if any.

        Example: `{{pre}}g 45`
        """
        if not game:
            game = models.Game.get_or_none(
                models.Game.category_id == ctx.channel.category_id
            )
            if not game:
                await ctx.send(
                    'No game specified and command not used in a game '
                    'category.'
                )
                return
        platform = 'Steam' if game.is_steam else 'Mobile'
        await ctx.send(embed=discord.Embed(
            title=game.name,
            description=(
                f'{game.member_count}/{game.space_count} players. '
                f'{platform} game.'
            ),
            colour=0xF58F29
        ).add_field(name='Players', value=game.player_list))

    @commands.command(
        brief='View open games.', name='open-games', aliases=['games', 'gs']
    )
    async def open_games(self, ctx: commands.Context):
        """View a list of open games.

        Example: `{{pre}}games`
        """
        lines = []
        for game in models.Game.select():
            if game.member_count < game.space_count:
                lines.append(
                    f'Game `{game.id:>3}`, `{game.member_count:>2}` players.'
                )
        await ctx.send('\n'.join(lines) or '*There\'s nothing here.*')
