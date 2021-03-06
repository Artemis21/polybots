"""JSON data model for bot settings."""
import json
import typing

from tools.datautils import jsondata


configdata = jsondata('data/config.json')

with open('config.json') as f:
    data = json.load(f)
    default_guild = data['guild']
    default_prefix = data['prefix']


class Config:
    """Data model for bot settings."""

    # Decorators moving cls arg to 2nd break pylint
    # pylint: disable=unsupported-assignment-operation,no-member

    @classmethod
    @configdata
    def get_prefix(data: typing.Dict, cls) -> str:    # noqa: ANN001
        """Get the prefix."""
        return data.get('prefix', default_prefix)

    @classmethod
    @configdata
    def set_prefix(data: typing.Dict, cls, prefix: str):    # noqa: ANN001
        """Set the prefix."""
        data['prefix'] = prefix

    @classmethod
    @configdata
    def get_guild(data: typing.Dict, cls) -> int:    # noqa: ANN001
        """Get the guild."""
        return data.get('guild', default_guild)

    @classmethod
    @configdata
    def set_guild(data: typing.Dict, cls, guild: int):   # noqa: ANN001
        """Set the guild."""
        data['guild'] = guild

    @classmethod
    @configdata
    def get_admins(data: typing.Dict, cls) -> typing.List[int]:
        """Get a list of admin users."""
        return data.get('admins', [])

    @classmethod
    @configdata
    def set_admins(data: typing.Dict, cls, admins: typing.List[int]):
        """Set the list of admin users."""
        data['admins'] = admins

    @classmethod
    @configdata
    def set_log_channel(data: typing.Dict, cls, channel: int):
        """Set the log channel."""
        data['log_channel'] = channel

    @classmethod
    @configdata
    def get_log_channel(data: typing.Dict, cls) -> int:
        """Get the log channel."""
        return data.get('log_channel', None)

    @classmethod
    @configdata
    def set_commands_channels(
            data: typing.Dict, cls, channels: typing.List[int]):
        """Add a commands channel."""
        data['commands_channels'] = ' '.join(map(str, channels))

    @classmethod
    @configdata
    def get_commands_channels(data: typing.Dict, cls) -> int:
        """Get the commands channels."""
        return list(map(int, data.get('commands_channels', '').split()))
