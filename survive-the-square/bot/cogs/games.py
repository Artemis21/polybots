"""Commands for manging an in progress game."""
from discord.ext import commands

from ..models import GameMember


class Games(commands.Cog):
    """Commands for managing an in progress game."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot

    @commands.command(brief='Message another player.', aliases=['m'])
    async def message(
            self, ctx: commands.Context, player: GameMember, *, message: str):
        """Message another player from your game.

        Example: `{{pre}}m artemis This is my message.`
        """
        dest = ctx.guild.get_channel(player.channel_id)
        webhook = None
        for existing_webhook in await dest.webhooks():
            if existing_webhook.user.id == self.bot.user.id:
                webhook = existing_webhook
        webhook = webhook or await dest.create_webhook(name='Messaging System')
        await webhook.send(
            content=message,
            username=ctx.author.display_name,
            avatar_url=ctx.author.avatar_url,
            files=[
                await attachment.to_file()
                for attachment in ctx.message.attachments
            ]
        )
