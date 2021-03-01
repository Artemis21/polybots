"""Commands for creating and viewing games."""
import discord
from discord.ext import commands

from main import checks, config, models


class Games(commands.Cog):
    """Commands for creating and viewing games."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot

    @commands.command(
        brief='Create a game.', name='new-game', aliases=['ng', 'new']
    )
    @checks.admin
    async def new_game(
            self, ctx: commands.Context, platform: str, limit: int = 14):
        """Create a new game, with an optional player limit (default 14).

        Examples:
        `{{pre}}new-game steam 8`
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
        game = models.Game.create(limit=limit, is_steam=is_steam)
        role = await ctx.guild.create_role(
            name=game.name, colour=discord.Colour(0xe4b400), mentionable=True
        )
        observer_role = ctx.guild.get_role(config.OBSERVER_ROLE_ID)
        category = await ctx.guild.create_category(name=game.name, overwrites={
            ctx.guild.default_role: discord.PermissionOverwrite(
                read_messages=False, send_messages=False),
            observer_role: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(
                read_messages=True, send_messages=True)
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
        if game.is_open:
            await game.add_player(ctx)
        else:
            await ctx.send(f'{game.name} is already closed, sorry.')

    @commands.command(
        brief='Leave a game.', name='leave-game', aliases=['l', 'leave']
    )
    async def leave_game(self, ctx: commands.Context, game: models.Game):
        """Leave a game you are in.

        Example: `{{pre}}leave 45`
        """
        if game.is_open:
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
        if not game.is_open:
            ctx.logger.log(f'Warning: {game.name} is closed.')
        await game.add_player(ctx, user)

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
        if not game.is_open:
            ctx.logger.log(f'Warning: {game.name} is closed.')
        await game.remove_player(ctx, user)

    @commands.command(
        brief='Re-open a game.', name='open-game',
        aliases=['open', 'reopen', 'reopen-game', 'o']
    )
    @checks.admin
    async def open_game(self, ctx: commands.Context, game: models.Game):
        """Re-open a game.

        Example: `{{pre}}reopen 54`
        """
        if game.is_open:
            await ctx.send(f'{game.name} is already open.')
        else:
            game.is_open = True
            game.save()
            await ctx.send(f'Reopened game {game.id}.')

    @commands.command(
        brief='Close a game.', name='close-game', aliases=['close', 'c']
    )
    @checks.admin
    async def close_game(self, ctx: commands.Context, game: models.Game):
        """Close a game.

        Example: `{{pre}}close 29`
        """
        if game.is_open:
            game.is_open = False
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
        open_status = 'still open' if game.is_open else 'closed'
        platform = 'Steam' if game.is_steam else 'Mobile'
        players = models.Player.select().join(models.GameMember).where(
            models.GameMember.game == game
        )
        player_lines = []
        for player in players:
            ign = player.steam_name if game.is_steam else player.mobile_name
            player_lines.append(
                f'<@{player.discord_id}> - `{ign}`'
            )
        players = '\n'.join(player_lines) or '*No-one yet*'
        await ctx.send(embed=discord.Embed(
            title=game.name,
            description=(
                f'{game.member_count}/{game.limit} players, {open_status}. '
                f'{platform} game.'
            ),
            colour=0xF58F29
        ).add_field(name='Players', value=players))

    @commands.command(
        brief='View open games.', name='open-games', aliases=['games', 'gs']
    )
    async def open_games(self, ctx: commands.Context):
        """View a list of open games.

        Example: `{{pre}}games`
        """
        lines = []
        for game in models.Game.select().where(
                models.Game.is_open == True):    # noqa:E712
            lines.append(
                f'Game `{game.id:>3}`, `{game.member_count:>2}` players.'
            )
        await ctx.send('\n'.join(lines) or '*There\'s nothing here.*')

    @commands.command(brief='Award a win.', aliases=['w', 'winner', 'winners'])
    @checks.admin
    async def win(
            self, ctx: commands.Context,
            *users: commands.Greedy[discord.Member]):
        """Award a win to one or more users.

        Example: `{{pre}}win @Artemis @Dorian @JBHoTep`
        """
        models.Player.give_many_wins([user.id for user in users])
        await ctx.send('Done!')
