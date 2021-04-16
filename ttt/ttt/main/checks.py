"""Discord.py command checks."""
from typing import Callable

from discord.ext import commands

from . import config
from ..models import Player


Check = Callable[[Callable], commands.Command]


def get_player(ctx: commands.Context) -> bool:
    """Get someone's player model if registered."""
    player = Player.get_or_none(Player.discord_id == ctx.author.id)
    if player:
        if ctx.guild and ctx.guild.id == config.BOT_GUILD_ID:
            player.reload_from_discord_member(ctx.author)
        ctx.ttt_player = player
    else:
        ctx.ttt_player = None
    return True


def optional_registered() -> Check:
    """Check that gets a player object if the player is registered."""
    return commands.check(get_player)


def registered() -> Check:
    """Create a check for registered players."""

    def is_registered(ctx: commands.Context) -> bool:
        """Check if someone is registered."""
        get_player(ctx)
        if ctx.ttt_player:
            return True
        raise commands.CommandError(
            f'You must be registered (`{ctx.prefix}register`) to use this '
            'command.'
        )

    return commands.check(is_registered)


def manager() -> Check:
    """Create a check for tournament managers."""

    def is_manager(ctx: commands.Context) -> bool:
        """Check if someone is a manager."""
        for role in ctx.author.roles:
            if role.id == config.BOT_ADMIN_ROLE_ID:
                return True
        raise commands.CommandError(
            'Only tournament managers can use this command.'
        )

    return commands.check(is_manager)


def caution() -> Check:
    """Create a check that asks users to confirm."""

    async def caution_check(ctx: commands.Context) -> bool:
        """Ask the user to confirm."""
        if getattr(ctx, 'help_command_check', False):
            return True
        await ctx.send(
            'Are you sure you want to procede? This cannot be undone. `Yes` '
            'to  continue, anything else to cancel.'
        )
        message = await ctx.bot.wait_for(
            'message', check=lambda m: (
                m.author == ctx.author and m.channel == ctx.channel
            )
        )
        if message.content.upper() != 'YES':
            await ctx.send('Cancelled.')
            return False
        return True

    return commands.check(caution_check)
