"""Checks to perform on users."""
from discord.ext import commands
import discord
import typing

from models.user import User
from models.settings import Settings


def registered() -> typing.Awaitable:
    """Wrapper for functions that should only be used by registered users."""
    async def check(ctx):
        ctx.giant_user = User.load(ctx.author.id)
        if not ctx.giant_user:
            await ctx.send(
                f'You must register first (`{ctx.prefix}register`).'
            )
            return False
        return True

    return commands.check(check)


def is_admin(user: discord.Member) -> bool:
    """Utility to check if someone is an admin."""
    if user.id in Settings.admin_users:
        return True
    for role in user.roles:
        if role.id in Settings.admin_roles:
            return True


def admin() -> typing.Awaitable:
    """Wrapper to check if someone is an admin."""
    async def check(ctx):
        if is_admin(ctx.author):
            return True
        else:
            await ctx.send('This is an admin only command.')
            return False

    return commands.check(check)
