"""Commands for viewing and managing games."""
import asyncio
import csv
import io
import logging
from datetime import datetime

import discord
from discord.ext import commands, tasks

from dateutil.parser import parse as parse_dt

from ..main import checks, config, logs, many, matchmaking, timeouts
from ..models import Game, GamePlayer, GameType, Player, Timeout


Ctx = commands.Context


def yes_or_no(value: bool) -> str:
    """Convert a boolean value to a human-readable string."""
    return 'Yes' if value else 'No'


class Games(commands.Cog):
    """Commands for viewing and managing games."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot
        self.ready = False

    @commands.Cog.listener()
    async def on_ready(self):
        """Start the recheck loop."""
        if not self.ready:
            self.recheck_games.start()
            self.ready = True

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Check for an ELO bot command being run."""
        if not message.content.startswith('$'):
            return
        command, *args = message.content[1:].split()
        if command not in ('win', 'unwin', 'rename', 'confirm'):
            return
        try:
            game_id = int(args[0])
        except (IndexError, ValueError):
            return
        game = Game.get_or_none(Game.elo_bot_id == game_id)
        if not game:
            return
        await logs.log(
            f'Game {game_id} mentioned, preparing to reload... '
            f'({message.jump_url})', logging.DEBUG
        )
        # Wait 5 seconds because ELO bot can be slow.
        await asyncio.sleep(5)
        await game.reload_from_elo_api()
        game.recheck_at = datetime.now() + config.ELO_RECHECK_TIME
        game.save()

    @tasks.loop(seconds=config.ELO_RECHECK_FREQUENCY.total_seconds())
    async def recheck_games(self):
        """Recheck all games with pending rechecks."""
        await Game.recheck_games()

    @commands.command(brief='View a game.', aliases=['g'])
    async def game(self, ctx: Ctx, game: Game):
        """View a game by it's ID.

        Example: `{{pre}}game 34`
        """
        await ctx.send(embed=game.embed())

    @commands.command(brief='View timeouts for a game.')
    async def timeouts(self, ctx: Ctx, game: Game):
        """View registered timeouts for a game.

        Example: `{{pre}}timeouts 53591`
        """
        await ctx.send(embed=timeouts.display_timeouts(game))

    @commands.command(brief='Report your loss.', aliases=['resign', 'l'])
    @checks.registered()
    async def loss(self, ctx: Ctx, game: Game):
        """Resign from a game your are in.

        YOU MUST HAVE ACTUALLY LOST OR RESIGNED.
        You do not have to do this if the game has already been marked as won.

        Example: `{{pre}}resign 82419`
        """
        member = game.get_member(ctx.ttt_player)
        if member:
            member.lost = True
            member.ended_at = datetime.now()
            member.save()
            await ctx.send(
                f'Marked you as having lost game {game.elo_bot_id}.'
            )
        else:
            await ctx.send(f'You are not in game {game.elo_bot_id}.')

    @commands.command(
        brief='Unmark a loss.', name='undo-loss', aliases=['unloss', 'ul']
    )
    @checks.manager()
    async def undo_loss(self, ctx: Ctx, game: Game, *, player: Player):
        """Undo a marked loss.

        Example: `{{pre}}unloss 82419 Artemis`
        """
        member = game.get_member(player)
        if member:
            member.lost = False
            member.save()
            await ctx.send(
                f'Set **{player.display_name}** as not having lost game '
                f'**{game.elo_bot_id}**.'
            )
        else:
            await ctx.send(
                f'**{player.display_name}** is not in game '
                f'**{game.elo_bot_id}**.'
            )

    @commands.command(
        brief='Delete a timeout.',
        name='delete-timeout', aliases=['del-to', 'dt']
    )
    @checks.manager()
    async def delete_timeout(self, ctx: Ctx, timeout: Timeout):
        """Delete a timeout by ID.

        Example: `{{pre}}del-to 24`
        """
        summary = timeout.get_summary()
        timeout.delete_instance()
        await ctx.send('Deleted timeout:\n> ' + summary)

    @commands.command(
        brief='View a game type.', name='game-type', aliases=['gt', 'type']
    )
    async def game_type(self, ctx: Ctx, game_type_id: int):
        """View a game type by ID.

        Example: `{{pre}}game-type 5`
        """
        if game_type := GameType.from_id(game_type_id):
            await ctx.send(embed=discord.Embed(
                title=f'Game type {game_type_id}',
                colour=config.COL_ACCENT,
                description=str(game_type)
            ))
        else:
            await ctx.send(f'No game type found by ID {game_type_id}.')

    @commands.command(brief='Report a timeout.', aliases=['red'])
    @checks.registered()
    async def timeout(self, ctx: Ctx, game: Game, *, player: Player):
        """Report a timeout for a player.

        You should also upload a screenshot proving it.

        Example: `{{pre}}timeout 849103 @Artemis` +1 attachment.
        """
        await ctx.send(timeouts.report_timeout(
            ctx, game, player, is_timeout=True
        ))

    @commands.command(brief='Report a semi-timeout.')
    @checks.registered()
    async def yellow(self, ctx: Ctx, game: Game, *, player: Player):
        """Report a player's timer going yellow.

        You should also upload a screenshot proving it.

        Example: `{{pre}}yellow 18345 @Ramano` +1 attachment.
        """
        await ctx.send(timeouts.report_timeout(
            ctx, game, player, is_timeout=False
        ))

    @commands.command(
        brief='Create a game.', name='open-game', aliases=['open', 'o']
    )
    @checks.manager()
    async def open_game(self, ctx: Ctx, *users: commands.Greedy[Player]):
        """Create a game.

        Example:
        `{{pre}}create 3 @Artemis @Ramana @Thorin @Legorooj`
        """
        if len(users) != 4:
            await ctx.send('Game must have four players.')
            return
        with ctx.typing():
            game = await Game.create_game(players=users, guild=ctx.guild)
        await ctx.send(f'Created game (`{game.elo_bot_id}`).')

    @commands.command(brief='Un-open a game.', aliases=['u', 'delete', 'd'])
    @checks.manager()
    async def unopen(self, ctx: Ctx, game: Game):
        """Delete an opened game.

        Example: `{{pre}}unopen 63404`
        """
        id = game.elo_bot_id
        for member in game.members:
            discord_user = ctx.bot.get_user(member.player.discord_id)
            if not discord_user:
                discord_user = await ctx.bot.fetch_user(
                    member.player.discord_id
                )
            await discord_user.send(f'Game {id} has been deleted.')
            member.delete_instance()
        game.delete_instance()
        await ctx.send(f'Deleted game {id}.')

    @commands.command(
        brief='Check player compatibility.',
        name='check-players', aliases=['check', 'c']
    )
    @checks.manager()
    async def check(self, ctx: Ctx, *, users: many.Many[Player]):
        """Check if some players can play together.

        Example:
        `{{pre}}check @Artemis @Ramana @Thorin @Legorooj`
        """
        compatibility = matchmaking.player_compatibility(users)
        await ctx.send(embed=discord.Embed(
            title='Player Compatibility Check',
            colour=config.COL_ACCENT,
            description=(
                f'**Games shared:** {compatibility.shared_games}\n'
                '**Can play new positions?** '
                f'{yes_or_no(compatibility.new_positions)}\n'
                '**Can play almost-new positions?** '
                f'{yes_or_no(compatibility.almost_new_positions)}\n'
                '**Any from same team?** '
                f'{yes_or_no(compatibility.common_teams)}'
            )
        ))

    @commands.command(
        brief='Open multiple games.', name='mass-open', aliases=['mo']
    )
    @checks.manager()
    async def mass_open(self, ctx: Ctx, *, users: many.Many[Player]):
        """Create many games for one round.

        `users` must be a multiple of four users.

        Example:
        `{{pre}}create 5 @a @b @c @d @1 @2 @3 @4 @i @ii @iii @iv`
        """
        groups = [users[start:start + 4] for start in range(0, len(users), 4)]
        if len(groups[-1]) != 4:
            await ctx.send('You must specify a multiple of four users.')
            return
        with ctx.typing():
            for group in groups:
                await Game.create_game(players=group, guild=ctx.guild)
        await ctx.send(f'Created {len(groups)} games.')

    @commands.command(brief='Set a game end date.', name='end-date')
    @checks.manager()
    async def end_date(self, ctx: Ctx, game: Game, *, date: parse_dt = None):
        """Set the end date for a game.

        This should not usually be necessary as it will be done when a game is
        autoconfirmed. Defaults to the current date.

        Example:
        `{{pre}}end-date 58183`
        `{{pre}}end-date 83914 20th June 2021 12:30`
        """
        date = date or datetime.now()
        game.won_at = date
        game.save()
        GamePlayer.update(ended_at=date).where(
            GamePlayer.game_id == game.elo_bot_id
        ).execute()
        await ctx.send(f'Set end date for {game.elo_bot_id} to {date}.')

    @commands.command(
        brief='Export games to CSV.', name='export-games', aliases=['eg'])
    @checks.manager()
    async def export_games(self, ctx: commands.Context):
        """Export a list of all games to CSV.

        Includes: Game ID, Map type, Tribe, Alternative tribe, Game name,
        End date.

        Example: `{{pre}}eg`
        """
        file = io.StringIO()
        writer = csv.writer(file)
        writer.writerow([
            'Game ID', 'Map type', 'Tribe', 'Alternative tribe', 'Game name',
            'End date'
        ])
        for game in Game.select():
            writer.writerow([
                game.elo_bot_id, game.game_type.map_type,
                str(game.game_type.tribe),
                str(game.game_type.alternative_tribe), game.game_name,
                game.won_at.isoformat() if game.won_at else '-'
            ])
        file.seek(0)
        await ctx.send(file=discord.File(file, filename='ttt_games.csv'))

    @commands.command(
        brief='Export game sides to CSV.', name='export-sides', aliases=['es'])
    @checks.manager()
    async def export_sides(self, ctx: commands.Context):
        """Export a list of all game sides to CSV.

        Includes: Game ID, User ID, win/loss, position.

        Example: `{{pre}}es`
        """
        file = io.StringIO()
        writer = csv.writer(file)
        writer.writerow([
            'Game ID', 'Player Discord ID', 'State', 'Position'
        ])
        for side in GamePlayer.select():
            state = (
                'won' if side.won else ('lost' if side.lost else 'incomplete')
            )
            writer.writerow([
                side.game_id, side.player_id, state, side.position
            ])
        file.seek(0)
        await ctx.send(file=discord.File(file, filename='ttt_sides.csv'))
