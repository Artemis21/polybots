from cogs.meta import Meta
from cogs.names import Names


def setup(bot):
    for i in (Names, Meta):
        bot.add_cog(i(bot))
