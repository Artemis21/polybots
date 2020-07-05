"""Discord.py command error handler."""
import re
import traceback

import discord
from discord.ext import commands


async def on_command_error(ctx: commands.Context, error: Exception):
    """Handle an error."""
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CheckFailure):
        return
    rawtitle = type(error).__name__
    rawtitle = re.sub('([a-z])([A-Z])', r'\1 \2', rawtitle)
    title = rawtitle[0].upper() + rawtitle[1:].lower()
    e = discord.Embed(
        colour=0xe94b3c, title=title, description=str(error)
    )
    await ctx.send(embed=e)
    if hasattr(error, 'original'):
        err = error.original
        traceback.print_tb(err.__traceback__)
        print(f'{type(err).__name__}: {err}.')
