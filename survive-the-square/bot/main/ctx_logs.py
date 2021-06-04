"""Discord.py Bot hooks that add a logger to Context.

Messages can be added to the log with a function, and are all sent once
the command has finished executing.
"""
from discord.ext import commands


class Logger:
    """A simple logger for Discord.py commands."""

    def __init__(self, ctx: commands.Context):
        """Set up the logger."""
        self.messages = []
        self.ctx = ctx

    def log(self, message: str):
        """Log a message."""
        self.messages.append(message)

    async def send(self):
        """Send all messages remaining in the logs."""
        if self.messages:
            await self.ctx.send('\n'.join(self.messages))
            self.messages = []


async def before_invoke(ctx: commands.Context):
    """Add a logger to the context."""
    ctx.logger = Logger(ctx)


async def after_invoke(ctx: commands.Context):
    """Output from the logger if anything is there."""
    await ctx.logger.send()


def setup(bot: commands.Bot):
    """Add the hooks to the bot."""
    bot.before_invoke(before_invoke)
    bot.after_invoke(after_invoke)
