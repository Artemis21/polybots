from .meta import Meta
from .games import Games, Modifiers
from .users import Details


def setup(bot):
    for i in (Games, Details, Modifiers, Meta):
        if (bot.use_cogs == []) or (i.__class__.__name__[3:] in bot.use_cogs):
            bot.add_cog(i(bot))
