from discord.ext import commands
from models import User


def registered():
    async def check(ctx):
        ctx.giant_user = User.load(ctx.author.id)
        if not ctx.giant_user:
            await ctx.send(
                f'You must register first (`{ctx.prefix}register`).'
            )
            return False
        return True
    return commands.check(check)


class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Set your code.')
    @registered()
    def setcode(self, ctx, code):
        """
        Set your friend ID so others can add you to games easily.
        Example:
        `{{pre}}setcode wDIIBFCiao73ogYu`
        """
        ctx.giant_user.code = code
        await ctx.send(f'Code set to `{code}`.')

    @commands.command(brief='Set your name.')
    @registered()
    def setname(self, ctx, *, name):
        """
        Set your in-game name so others can recognise you in-game.
        Example:
        `{{pre]}setname artemisdev`
        `{{pre}}setname My Name`
        """
        ctx.giant_user.name = name
        await ctx.send(f'In-game name set to `{name}`.')
