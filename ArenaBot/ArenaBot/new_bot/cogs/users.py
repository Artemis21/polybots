from discord.ext import commands
import discord
from models.users import Users
from utils.paginator import DescPaginator


class Players(commands.Cog):
    '''View user details including timezone, friend code and points.
    '''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='View all users.', aliases=['lb', 'leaders'])
    async def leaderboard(self, ctx):
        '''View the leaderboard, sorted by points.
        '''
        lines = []
        n = 1
        for user in sorted(Users.users, key=lambda x: x.points, reverse=True):
            lines.append(f'**#{n}:** {user.user} ({user.points})')
            n += 1
        desc = '\n'.join(lines)
        pag = DescPaginator(ctx, 'Leaderboard', desc, 0x00ff00, 20)
        await pag.setup()

    @commands.command(brief='View a user.')
    async def player(self, ctx, user: discord.Member=None):
        '''View a users points, timezone, tier and current game (if any).
        Defaults to yourself.
        '''
        if not user:
            user = ctx.author
        user = await Users.get_user(user)
        e = discord.Embed(title=user, desc=user.tierrole.mention)
        e.add_field(name='Points', value=user.points)
        e.add_field(name='Timezone', value=user.tz)
        game = 'N/A'
        if user.game:
            game = user.game.channel.mention
        e.add_field(name='Game', value=game)
        await ctx.send(embed=e)

    @commands.command(brief='Get a friend code.')
    async def code(self, ctx, user: discord.Member=None):
        '''View a users polytopia friend code. Defaults to your own.
        '''
        if not user:
            user = ctx.author
        await ctx.send(f'Friend code for {user}:')
        user = await Users.get_user(user)
        await ctx.send(f'`{user.code}`')

    @commands.command(brief='Set your timezone.', aliases=['tz'])
    async def timezone(self, ctx, timezone: int):
        '''Set your timezone. This should be a UTC offset. Examples:
        `{{pre}}timezone 0` (UTC)
        `{{pre}}timezone -4` (UTC-4)
        `{{pre]}timezone 7` (UTC+7)
        '''
        if -24 > timezone or 24 < timezone:
            return await ctx.send('That\'s not a timezone!')
        user = await Users.get_user(user)
        timezone = str(timezone)
        if timezone[0] not in '+-':
            timezone = '+' + timezone
        user.tz = 'UTC' + timezone
        await ctx.send(f'Timezone set to {user.tz}.')

    @commands.command(brief='Set your friend code.')
    async def setcode(self, ctx, code):
        '''Set your friend code.
        '''
        user = await Users.get_user(user)
        user.code = code
        await ctx.send('Code set successfully.')
