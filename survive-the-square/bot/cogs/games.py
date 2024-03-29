"""Commands for manging an in progress game."""
import discord
from discord.ext import commands

from ..main import checks
from ..models import Game, GameMember


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
            avatar_url=str(ctx.author.avatar),
            files=[
                await attachment.to_file()
                for attachment in ctx.message.attachments
            ]
        )
        await ctx.message.add_reaction(u'\u2705')    # Check mark.

    @commands.command(brief='Observe a game.', aliases=['o'])
    async def observe(self, ctx: commands.Context, game: Game):
        """Get the observer role for a game.

        Example: `{{pre}}observe 12`
        """
        member = GameMember.get_or_none(
            GameMember.game_id == game.id,
            GameMember.player_id == ctx.author.id
        )
        if member:
            await ctx.send('You cannot observe a game you are in.')
            return
        role = ctx.guild.get_role(game.observer_role_id)
        if not role:
            await ctx.send('The observer role for this game has been deleted :(')
            return
        await ctx.author.add_roles(role)
        await ctx.send('Gave you the role.')

    @commands.command(brief='Archive a game.')
    @checks.admin
    async def archive(self, ctx: commands.Context, game: Game):
        """Archive a game's channels.

        Example: `{{pre}}archive 3`
        """
        async with ctx.typing():
            for role_id in game.role_ids:
                role = ctx.guild.get_role(role_id)
                if role:
                    await role.delete()
            for channel_id in game.channel_ids:
                channel = ctx.guild.get_channel(channel_id)
                if channel:
                    await channel.edit(
                        overwrites={
                            ctx.guild.default_role: discord.PermissionOverwrite(
                                read_messages=False, send_messages=False
                            )
                        }
                    )
            category = ctx.guild.get_channel(game.category_id)
            await category.edit(name=category.name + ' - Archived')
            GameMember.delete().where(GameMember.game == game).execute()
            game.delete_instance()
        await ctx.send('Game archived.')

    @commands.command(brief='Delete a game.')
    @checks.admin
    async def delete(self, ctx: commands.Context, game: Game):
        """Delete a game and it's channels.

        Example: `{{pre}}delete 3`
        """
        async with ctx.typing():
            for channel_id in game.channel_ids:
                channel = ctx.guild.get_channel(channel_id)
                if channel:
                    await channel.delete()
            for role_id in game.role_ids:
                role = ctx.guild.get_role(role_id)
                if role:
                    await role.delete()
            GameMember.delete().where(GameMember.game == game).execute()
            game.delete_instance()
        await ctx.send('Game deleted.')
