"""Utility for mass adding of roles."""
import discord

import typing


async def massrole(role: discord.Role, members: typing.List[discord.Member]):
    """Award a role to a list of people."""
    for member in members:
        await member.add_roles(role)
