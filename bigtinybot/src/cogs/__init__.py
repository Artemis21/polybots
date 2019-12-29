from cogs.teams import Teams, Admin
from cogs.meta import Meta


def setup(bot):
    for i in (Teams, Admin, Meta):
        bot.add_cog(i(bot))
