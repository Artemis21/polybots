"""Wrapper for the config model."""
import typing

import discord

from models import Config as ConfigModel

from tools.datautils import discorddata


class Config:
    """Wrapper for the config model."""

    # Decorators moving cls/self arg to 2nd break pylint
    # pylint: disable=no-value-for-parameter,no-self-argument,no-member

    @property
    def prefix(self) -> str:
        """Get the prefix."""
        return ConfigModel.get_prefix()

    @prefix.setter
    def prefix(self, prefix: str):
        """Set the prefix."""
        ConfigModel.set_prefix(prefix)

    @property
    @discorddata
    def guild(client: discord.Client, self) -> typing.Optional[discord.Guild]:    # noqa: ANN001,E501
        """Get the guild."""
        guild_id = ConfigModel.get_guild()
        return client.get_guild(guild_id)

    @guild.setter
    def guild(self, guild: discord.Guild):
        """Set the guild."""
        ConfigModel.set_guild(guild.id)

    @property
    def admins(self) -> typing.List[discord.Member]:
        """Get the list of admin users."""
        guild = self.guild
        if not guild:
            return
        raw = ConfigModel.get_admins()
        admins = []
        for user_id in raw:
            user = guild.get_member(user_id)
            if user:
                admins.append(user)
        return admins

    @admins.setter
    def admins(self, admins: typing.List[discord.User]):
        """Set the list of admin users."""
        raw = [user.id for user in admins]
        ConfigModel.set_admins(raw)

    @property
    def log_channel(self) -> typing.Optional[discord.TextChannel]:
        """Get the log channel."""
        channel_id = ConfigModel.get_log_channel()
        guild = self.guild
        if guild:
            return guild.get_channel(channel_id)

    @log_channel.setter
    def log_channel(self, channel: discord.TextChannel):
        """Set the log channel."""
        ConfigModel.set_log_channel(channel.id)

    @property
    def commands_channels(self) -> typing.List[discord.TextChannel]:
        """Get the commands channels."""
        channel_ids = ConfigModel.get_commands_channels()
        guild = self.guild
        channels = []
        if guild:
            for cid in channel_ids:
                channels.append(guild.get_channel(cid))
        return channels

    def add_commands_channel(self, channel: discord.TextChannel):
        """Add a commands channel."""
        channel_ids = ConfigModel.get_commands_channels()
        channel_ids.append(channel.id)
        ConfigModel.set_commands_channels(channel_ids)

    def remove_commands_channel(self, channel: discord.TextChannel):
        """Remove a commands channel."""
        channel_ids = ConfigModel.get_commands_channels()
        channel_ids = [cid for cid in channel_ids if cid != channel.id]
        ConfigModel.set_commands_channels(channel_ids)
