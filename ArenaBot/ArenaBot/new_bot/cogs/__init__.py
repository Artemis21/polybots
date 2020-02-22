from cogs.meta import Meta
from cogs.users import Players
from cogs.modifiers import Modifiers
from cogs.settings import Settings
from cogs.games import Games


def setup(bot):
    for i in (Games, Players, Modifiers, Settings, Meta):
        bot.add_cog(i(bot))
