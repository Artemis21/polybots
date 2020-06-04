"""Discord.py command error handler."""
import re
import traceback

import discord
from discord.ext.commands import Context

from tools import colours


async def on_command_error(ctx: Context, error: Exception):
    """Handle an error."""
    rawtitle = type(error).__name__
    rawtitle = re.sub('([a-z])([A-Z])', r'\1 \2', rawtitle)
    title = rawtitle[0].upper() + rawtitle[1:].lower()
    e = discord.Embed(
        colour=colours.ERROR, title=title, description=str(error)
    )
    await ctx.send(embed=e)
    if hasattr(error, 'original'):
        err = error.original
        traceback.print_tb(err.__traceback__)
        print(f'{type(err).__name__}: {err}.')
