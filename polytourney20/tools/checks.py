"""Discord.py command checks."""
import typing

import discord
from discord.ext import commands

from tools.config import Config


config = Config()


def _is_in_list(
        user: discord.User, users: typing.List[discord.Member]
        ) -> bool:
    """Check if a user is in a list of users."""
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


def commands_channel() -> commands.check:
    """Check for commands channel-only commands."""
    async def check(ctx):
        if ctx.channel in config.commands_channels:
            return True
        if ctx.help_command_check:
            return False
        await ctx.send(
            f'{ctx.author.mention}, this command should only be used in '
            f'{config.commands_channels[0].mention}.',
            delete_after=3
        )
        await ctx.message.delete(delay=3)
        return False
    return commands.check(check)


def disabled() -> commands.check:
    """Check for disabled commands."""
    async def check(ctx):
        if ctx.help_command_check:
            return False
        await ctx.send(
            'This command is temporarily disabled due to techinal issues. '
            'Sorry.'
        )
        return False
    return commands.check(check)
