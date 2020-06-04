from discord.ext import commands
import typing
import discord
import string

from models.user import User
from models.settings import Settings
from tools.checks import registered, admin


def divisions_in_league(league):
    num = 2 ** league
    return list(string.ascii_uppercase[:num])


class Users(commands.Cog):
    """Commands relating to individual users."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Set your code.')
    @registered()
    async def setcode(self, ctx, code):
        """
        Set your friend ID so others can add you to games easily.
        Example:

        `{{pre}}setcode wDIIBFCiao73ogYu`
        """
        ctx.giant_user.code = code
        await ctx.send(f'Code set to `{code}`.')

    @commands.command(brief='Set your name.')
    @registered()
    async def setname(self, ctx, *, name):
        """
        Set your in-game name so others can recognise you in-game.

        Example:
        `{{pre]}setname artemisdev`
        `{{pre}}setname My Name`
        """
        ctx.giant_user.name = name
        await ctx.send(f'In-game name set to `{name}`.')

    @commands.command(brief='View a code.')
    async def code(self, ctx, *, user: discord.Member=None):
        """
        View someone's friend ID. Defualts to your own.

        Examples:
        `{{pre}}code @Artemis`
        `{{pre}}code`
        """
        user = user or ctx.author
        user_data = User.load(user.id)
        if user_data:
            await ctx.send(f'Code for {user}:')
            await ctx.send(f'`{user_data.code}`')
        else:
            await ctx.send(f'{user} is not registered in the bot.')

    @commands.command(brief='Drop out of the league.')
    @registered()
    async def quit(self, ctx):
        """
        Drop out of the league. Use with caution and only when absolutely necessarry.

        Example:
        `{{pre}}quit`
        """
        await ctx.send('Are you sure you want to drop out of the league?')
        mes = await ctx.bot.wait_for('message', check=(
            lambda: (
                mes.channel.id == ctx.channel.id 
                and mes.author.id == ctx.author.id
            )
        ))
        if mes.content.lower() == 'yes':
            ctx.giant_user.delete()
            await ctx.send('Goodbye :cry:')
        else:
            await ctx.send('Cancelled.')

    @commands.command(brief='View a user.')
    async def user(self, ctx, *, user: discord.Member=None):
        """
        View a user's in game name, points, division etc. Defaults to yourself.

        Examples:
        `{{pre}}user Ymiros`
        `{{pre}}user`
        """
        d_user = user or ctx.author
        user = User.load(d_user.id)
        if not user:
            await ctx.send(f'{user} is not registered in the bot.')
        e = discord.Embed(title=user.name, description=f'`{user.code}`')
        e.set_thumbnail(url=d_user.avatar_url)
        e.add_field(name='In game name', value=user.name)
        e.add_field(name='Friend code', value=user.code)
        e.add_field(name='Points', value=user.points)
        e.add_field(name='Division', value=user.division)
        e.add_field(name='League', value=user.league)
        await ctx.send(embed=e)

    @commands.command(brief="Change someone's division.")
    @admin()
    async def division(self, ctx, division, *, user: discord.Member):
        """
        Set a player's division.

        Examples:
        `{{pre}}division C @Artemis`
        `{{pre}}division A @Karuin33`

        Also see: `{{pre}}league`
        """
        user_data = User.load(user.id)
        if user_data:
            division = division.upper()
            divisions = divisions_in_league(user_data.league)
            if division not in divisions:
                return await ctx.send(
                    f'There is no divison `{division}` in leage `'
                    f'{user_data.league}`.'
                )
            user_data.division = division
            await ctx.send(f'**{user.name}** is now in division {division}.')
        else:
            await ctx.send(f'**{user.name}** is not registered.')

    @commands.command(brief='Ban a user or role.')
    @admin()
    async def ban(
            self, ctx, *, target: typing.Union[discord.Role, discord.Member]
            ):
        """
        Ban a user or role from the league.

        Examples:
        `{{pre}}ban @Banned`
        `{{pre}}ban @gulord666`
        """
        if isinstance(target, discord.Member):
            l = Settings.banned_users
        else:
            l = Settings.banned_roles
        if target.id in l:
            return await ctx.send(f'**{target.name}** is already banned.')
        l.append(target)
        if isinstance(target, discord.Member):
            user_data = User.load(target.id)
            if user_data:
                user_data.delete()
        else:
            for user in target.members:
                user_data = User.load(user.id)
                if user_data:
                    user_data.delete()
        await ctx.send(f'**{target.name}** successfully banned.')

    @commands.command(brief="Modify someone's points.")
    @admin()
    async def givepoints(self, ctx, user: discord.Member, points: int):
        """
        Edit a player's points.

        Examples:
        `{{pre}}givepoints @Artemis 10`
        `{{pre}}givepoints @MPHuot -5`
        """
        user_data = User.load(user.id)
        if user_data:
            user_data.points += points
            await ctx.send(f'**{user.name}** now has {user_data.points} points.')
        else:
            await ctx.send(f'**{user.name}** is not registered.')

    @commands.command(brief="Modify someone's name.")
    @admin()
    async def adminsetname(self, ctx, user: discord.Member, *, name: str):
        """
        Edit a player's in game name.

        Examples:
        `{{pre}}adminsetname @Artemis artemisdev`
        `{{pre}}adminsetname @Bush In Game Name`
        """
        user_data = User.load(user.id)
        if user_data:
            user_data.name = name
            await ctx.send(f"**{user.name}**'s name is now {name}.")
        else:
            await ctx.send(f'**{user.name}** is not registered.')

    @commands.command(brief="Modify someone's code.")
    @admin()
    async def adminsetcode(self, ctx, user: discord.Member, *, code: str):
        """
        Edit a player's friend ID.

        Examples:
        `{{pre}}adminsetcode @Artemis wDIIBFCiao73ogYu`
        `{{pre}}adminsetname @jamiepr 987mioOxO1lLLmdn`
        """
        user_data = User.load(user.id)
        if user_data:
            user_data.code = code
            await ctx.send(f"**{user.name}**'s friend ID is now {code}.")
        else:
            await ctx.send(f'**{user.name}** is not registered.')



# TODO: Register command
# TODO: Change league command (admin)
# These require understanding of how the leagues are balanced.
