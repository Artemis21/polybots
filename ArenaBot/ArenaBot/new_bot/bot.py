from discord.ext import commands, tasks
import discord
from utils import errors
import traceback as tb
import asyncio
import models
from models.config import Config


class ArenaBot(commands.Bot):
    def __init__(self, prefix, test=False, cogs=[]):
        super().__init__(command_prefix=prefix)
        self.pre = prefix
        self.test = test
        self.use_cogs = cogs
        self.ready = False

    async def guild_check(self, ctx):
        return ctx.guild == Config.guild

    async def on_ready(self):
        if self.ready:
            return
        models.load(self)
        self.add_check(self.guild_check)
        self.load_extension('cogs')
        self.save.start()
        self.ready = True
        print(f'Logged in as {self.user}.')
        act1 = discord.Activity(
            name=f'{Config.prefix}help.',
            type=discord.ActivityType.listening
        )
        act2 = discord.Activity(
            name='everything you say.',
            type=discord.ActivityType.listening
        )
        acts = ((act1, 6), (act2, 6))
        n = 0
        while True:
            act1.name = f'{Config.prefix}help.'
            await self.change_presence(activity=acts[n][0])
            n += 1
            n %= len(acts)
            await asyncio.sleep(acts[n][1])

    @tasks.loop(minutes=1)
    async def save(self):
        models.save()

    async def close(self):
        models.save()
        await super().close()

    async def on_command_error(self, ctx, error):
        if self.test:
            try:
                tb.print_tb(error.original.__traceback__)
            except AttributeError:
                pass
        await errors.handle(error, ctx)
