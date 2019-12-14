from ..models import details
from ..utils import checks
from discord.ext import commands, tasks
import discord


class Tourney(commands.Cog):
    '''Info on teams and the tourney.
    '''
    def __init__(self, bot):
        self.bot = bot
        self.data = details.Teams
        self.data.load()

    async def handle_sm(self, ctx, s, m):
        if type(m) == discord.Embed:
            return await ctx.send(embed=e)
        if s:
            await ctx.send(f'Success: {m}')
        else:
            await ctx.send(f'Error: {m}')

    async def caution(self, ctx):
        await ctx.send(
            'Are you sure you wish to procede? This cannot be undone. `Yes` to'
            ' continue, anything else to cancel.'
        )

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        mes = await self.bot.wait_for('message', check=check)
        if mes.content.upper() != 'YES':
            await ctx.send('Cancelled.')
            return False
        return True

    @commands.command(brief='Register your team.')
    async def register(self, ctx, name, partner: discord.Member):
        '''Register a team to take part in the tourney.
        `name` is the name of the team. `partner` is you teammate.
        IMPORTANT: at the time of signing up, your local ELO + your \
        teammate's local ELO *must* be less than 2550!
        '''
        s, m = self.data.add_team(name, (ctx.author, partner), self.bot)
        await self.handle_sm(ctx, s, m)

    @commands.command(brief='Delete a team.')
    async def quit(self, ctx, team_id=None):
        '''Remove a team from the tourny. Only tournament admins may remove
        someone elses team.
        `team_id` is the id of the team to delete, defaults to the team you \
        are in.
        '''
        if not await self.caution(ctx):
            return
        if checks.admin(ctx.author) and team_id:
            return await self.handle_sm(*self.data.remove_team(team_id))
        game = self.data.get_by_member(ctx.author)
        if not game:
            return await ctx.send('You\'re not even in the tourney!')
        return await self.handle_sm(*self.data.remove_team(game.team_id))

    @commands.command(brief='View a team.')
    async def team(self, ctx, team_id=None):
        '''View the details of a team.
        `team_id` is the id of the team to view, defaults to the team you \
        are in.
        '''
        if not team_id:
            game = self.data.get_by_member(ctx.author)
            if not game:
                return await ctx.send('No game found...')
            team_id = game.team_id
        await self.handle_sm(*self.data.team_details(team_id))

    @commands.command(brief='View all teams.')
    async def teams(self, ctx):
        '''View a list of every team, including remaning lives, team name and \
        team ID.
        '''
        lines = ['```']
        for i in self.data.teams:
            lines.append(
                f'**{i.name:>10}** (ID {i.team_id}): {i.lives} lives remaining'
            )
        await ctx.send('\n'.join(lines) + '```')

    @commands.command(brief='View tourney details.')
    async def tourney(self, ctx):
        '''View the current state of the tournament.
        '''
        await ctx.send(self.details())

    @commands.command(brief='Record a loss.')
    async def loss(self, ctx, team_id=None):
        '''Record a loss. This may either be done by the loosing team or a \
        tournament admin.
        '''
        if not await self.caution(ctx):
            return
        if checks.admin(ctx.author) and team_id:
            return await self.handle_sm(*self.data.give_loss(team_id))
        game = self.data.get_by_member(ctx.author)
        if not game:
            return await ctx.send('You\'re not even in the tourney!')
        return await self.handle_sm(*self.data.give_loss(game.team_id))

    @commands.command(brief='Open the tourney.')
    async def open_signups(self, ctx):
        '''Open signups for the tourney. This may only be done by a tourney \
        admin and may only be done once - proceed with caution!
        '''
        if not checks.admin(ctx.author):
            return await ctx.send('You must be an admin to run this command!')
        if not await self.caution(ctx):
            return
        await self.handle_sm(*self.data.open())

    @commands.command(brief='Start the tourney.')
    async def start_tourney(self, ctx):
        '''Let the tourney begin! This may only be done by a tourney \
        admin and may only be done once - proceed with caution!
        '''
        if not checks.admin(ctx.author):
            return await ctx.send('You must be an admin to run this command!')
        if not await self.caution(ctx):
            return
        await self.handle_sm(*self.data.start())

    @commands.command(brief='Reset the tourney.')
    async def reset(self, ctx):
        '''Delete all tourney data. This may only be done by a tourney \
        admin and is irreversible - proceed with caution!
        '''
        if not checks.admin(ctx.author):
            return await ctx.send('You must be an admin to run this command!')
        if not await self.caution(ctx):
            return
        self.data.reset()
        await ctx.send('And with a "Poof!" all their data was gone.')
