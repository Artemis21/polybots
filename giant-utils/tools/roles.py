"""Utility for mass adding of roles."""
import discord

import typing


async def mass_role(role: discord.Role, members: typing.List[discord.Member]):
    """Award a role to a list of people."""
    for member in members:
        await member.add_roles(role)


async def mass_un_role(role: discord.Role):
    """Remove a role from everyone who has it."""
    for member in role.members:
        await member.remove_roles(role)
