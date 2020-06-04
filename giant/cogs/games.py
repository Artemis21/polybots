"""The games cog."""
from discord.ext import commands

from tools.checks import registered, admin
from models.game import Game
from models.settings import Settings


class Games(commands.Cog):
    """Commands relating to games."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Start a game.')
    @registered()
    async def startgame(self, ctx, *, name):
        """Start the game you are hosting this round.

        Example: `{{pre}}startgame Winter of Fire`
        """
        # TODO: validate
        game = Game.create(
            ctx.author.id, ctx.giant_user.division, ctx.giant_user.league,
            Settings.season
        )
        # TODO: create channel
        # TODO: feedback
