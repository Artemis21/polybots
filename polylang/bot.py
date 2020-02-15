from discord.ext import commands
import discord
from utils import errors
import traceback as tb
import asyncio


class PolyLang(commands.Bot):
    def __init__(self, prefix, test=False, cogs=[]):
        super().__init__(command_prefix=prefix)
        self.pre = prefix
        self.test = test
        self.use_cogs = cogs
        self.load_extension('cogs')

    async def on_ready(self):
        act1 = discord.Activity(
            name=f'{self.command_prefix}help.',
            type=discord.ActivityType.listening
        )
        act2 = discord.Activity(
            name='Polytopia.',
            type=discord.ActivityType.playing
        )
        acts = ((act1, 6), (act2, 6))
        n = 0
        while True:
            act1.name = f'{self.command_prefix}help.'
            await self.change_presence(activity=acts[n][0])
            n += 1
            n %= len(acts)
            await asyncio.sleep(acts[n][1])

    async def on_command_error(self, ctx, error):
        if self.test:
            try:
                tb.print_tb(error.original.__traceback__)
            except AttributeError:
                pass
        await errors.handle(error, ctx)
