"""Discord.py command checks."""
from discord.ext import commands

from . import config


admin = commands.check_any(
    commands.is_owner(),
    commands.has_guild_permissions(manage_channels=True),
    commands.has_any_role(*config.ADMIN_ROLE_IDS)
)
