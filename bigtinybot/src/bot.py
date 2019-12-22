from discord.ext import commands
import discord
from utils import errors
import traceback as tb
import asyncio
from utils import checks


class BigTinyBot(commands.Bot):
    def __init__(self, prefix, test=False, cogs=[]):
        super().__init__(command_prefix=prefix)
        self.pre = prefix
        self.test = test
        self.use_cogs = cogs
        self.load_extension('cogs')
        # self.add_check(checks.channel)

    async def on_ready(self):
        act1 = discord.Activity(
            name=f'{self.command_prefix}help.',
            type=discord.ActivityType.listening
        )
        act2 = discord.Activity(
            name='polytopia.',
            type=discord.ActivityType.playing
        )
        acts = (act1, act2)
        n = 0
        while True:
            act1.name = f'{self.command_prefix}help.'
            await self.change_presence(activity=acts[n])
            n += 1
            n %= len(acts)
            await asyncio.sleep(6)

    async def on_command_error(self, ctx, error):
        if self.test:
            try:
                tb.print_tb(error.original.__traceback__)
            except AttributeError:
                pass
        await errors.handle(error, ctx)
