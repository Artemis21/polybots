from cogs.teams import Tourney
from cogs.meta import Meta


def setup(bot):
    for i in (Tourney, Meta):
        bot.add_cog(i(bot))
