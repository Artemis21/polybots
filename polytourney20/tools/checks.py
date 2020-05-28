"""Discord.py command checks."""
import typing

import discord
from discord.ext import commands

from tools.config import Config


config = Config()


def _is_in_list(
        user: discord.User, users: typing.List[discord.Member]
        ) -> bool:
    """Check if a user has any of a list of roles."""
    for authorised in users:
        if user.id == authorised.id:
            return True
    return False


def is_admin(user: discord.Member) -> bool:
    """Check if someone is an admin."""
    return _is_in_list(user, config.admins)


def admin() -> commands.check:
    """Check for admin-only commands."""
    return commands.check(lambda ctx: is_admin(ctx.author))
