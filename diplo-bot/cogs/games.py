"""Commands for creating and viewing games."""
import discord
from discord.ext import commands

from main import models


class Games(commands.Cog):
    """Commands for creating and viewing games."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot

    @commands.command(
        brief='Create a game.', name='new-game', aliases=['ng', 'new']
    )
    @commands.has_guild_permissions(administrator=True)
    async def new_game(self, ctx: commands.Context, limit: int = 14):
        """Create a new game, with an optional player limit (default 14).

        Example: `{{pre}}new-game 8`
        """
        game = models.Game.create(limit=limit)
        role = await ctx.guild.create_role(name=game.name)
        category = await ctx.guild.create_category(name=game.name, overwrites={
            ctx.guild.default_role: discord.PermissionOverwrite(
                read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True)
        })
        for channel in ('chat', 'role-play', 'policies', 'newsstand'):
            await category.create_text_channel(name=channel)
        game.role_id = role.id
        game.category_id = category.id
        game.save()
        await ctx.send(f'Created game {game.id}.')

    @commands.command(
        brief='Join a game.', name='join-game', aliases=['j', 'join']
    )
    async def join_game(self, ctx: commands.Context, game: models.Game):
        """Join a game by its ID.

        Example: `{{pre}}join 30`
        """
        if not game.open:
            await ctx.send(f'{game.name} is already closed, sorry.')
            return
        player = models.Player.get_player(ctx.author.id)
        if not game.get_member(player):
            models.GameMember.create(player=player, game=game)
            role = ctx.guild.get_role(game.role_id)
            await ctx.author.add_roles(role)
            await ctx.send(f'Added you to game {game.id}.')
            if game.member_count >= game.limit:
                game.open = False
                game.save()
                await ctx.send(f'{game.name} full. Game closed.')
        else:
            await ctx.send(f'You are already in game {game.id}.')

    @commands.command(
        brief='Leave a game.', name='leave-game', aliases=['l', 'leave']
    )
    async def leave_game(self, ctx: commands.Context, game: models.Game):
        """Leave a game you are in.

        Example: `{{pre}}leave 45`
        """
        if not game.open:
            await ctx.send(
                f'{game.name} is closed. Contact an admin to remove you.'
            )
            return
        player = models.Player.get_player(ctx.author.id)
        if member := game.get_member(player):
            member.delete_instance()
            role = ctx.guild.get_role(game.role_id)
            await ctx.author.remove_roles(role)
            await ctx.send(f'Removed you from game {game.id}.')
        else:
            await ctx.send(f'You are not in game {game.id}.')

    @commands.command(
        brief='Add a user to a game.', name='add-member', aliases=['a', 'add']
    )
    @commands.has_guild_permissions(administrator=True)
    async def add_member(
            self, ctx: commands.Context, user: discord.Member,
            game: models.Game):
        """Manually add a user to a game.

        Example: `{{pre}}add @Artemis 35`
        """
        if not game.open:
            await ctx.send(f'Warning: {game.name} is closed.')
            return
        player = models.Player.get_player(user.id)
        if not game.get_member(player):
            models.GameMember.create(player=player, game=game)
            role = ctx.guild.get_role(game.role_id)
            await user.add_roles(role)
            await ctx.send(f'Added {user.display_name} to game {game.id}.')
            if game.member_count >= game.limit:
                game.open = False
                game.save()
                await ctx.send(f'{game.name} full. Game closed.')
        else:
            await ctx.send(
                f'{user.display_name} is already in game {game.id}.'
            )

    @commands.command(
        brief='Remove a user from a game.', name='remove-member',
        aliases=['r', 'remove']
    )
    @commands.has_guild_permissions(administrator=True)
    async def remove_member(
            self, ctx: commands.Context, user: discord.Member,
            game: models.Game):
        """Manually remove a user from a game.

        Example: `{{pre}}remove @Artemis 31`
        """
        if not game.open:
            await ctx.send(f'Warning: {game.name} is closed.')
            return
        player = models.Player.get_player(user.id)
        if member := game.get_member(player):
            member.delete_instance()
            role = ctx.guild.get_role(game.role_id)
            await user.remove_roles(role)
            await ctx.send(f'Removed {user.display_name} from game {game.id}.')
        else:
            await ctx.send(
                f'{user.display_name} isn\'t in game {game.id}.'
            )

    @commands.command(
        brief='Re-open a game.', name='open-game',
        aliases=['open', 'reopen', 'reopen-game', 'o']
    )
    @commands.has_guild_permissions(administrator=True)
    async def open_game(self, ctx: commands.Context, game: models.Game):
        """Re-open a game.

        Example: `{{pre}}reopen 54`
        """
        if game.open:
            await ctx.send(f'{game.name} is already open.')
        else:
            game.open = True
            game.save()
            await ctx.send(f'Reopened game {game.id}.')

    @commands.command(
        brief='Close a game.', name='close-game', aliases=['close', 'c']
    )
    @commands.has_guild_permissions(administrator=True)
    async def close_game(self, ctx: commands.Context, game: models.Game):
        """Close a game.

        Example: `{{pre}}close 29`
        """
        if game.open:
            game.open = False
            game.save()
            await ctx.send(f'Closed game {game.id}.')
        else:
            await ctx.send(f'{game.name} is already closed.')

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
        open_status = 'still open' if game.open else 'closed'
        await ctx.send(embed=discord.Embed(
            title=game.name,
            description=(
                f'{game.member_count}/{game.limit} players, {open_status}.'
            )
        ))

    @commands.command(
        brief='View open games.', name='open-games', aliases=['games', 'gs']
    )
    async def open_games(self, ctx: commands.Context):
        """View a list of open games.

        Example: `{{pre}}games`
        """
        lines = []
        for game in models.Game.select().where(
                models.Game.open == True):    # noqa:E712
            lines.append(
                f'Game `{game.id:>3}`, `{game.member_count:>2}` players.'
            )
        await ctx.send('\n'.join(lines) or '*There\'s nothing here.*')
