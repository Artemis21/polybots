"""Discord.py command error handler."""
import re
import traceback

import discord
from discord.ext.commands import Context


async def on_command_error(ctx: Context, error: Exception):
    """Handle an error."""
    raw_title = type(error).__name__
    raw_title = re.sub('([a-z])([A-Z])', r'\1 \2', raw_title)
    title = raw_title[0].upper() + raw_title[1:].lower()
    e = discord.Embed(
        colour=0xe94b3c, title=title, description=str(error)
    )
    await ctx.send(embed=e)
    if hasattr(error, 'original'):
        err = error.original
        traceback.print_tb(err.__traceback__)
        print(f'{type(err).__name__}: {err}.')
