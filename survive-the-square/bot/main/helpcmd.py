"""Discord.py help command."""
import typing

import discord
from discord.ext import commands


class Help(commands.DefaultHelpCommand):
    """The help command."""

    brief = 'Shows this message.'
    help = (
        'Get help on the bot, a command or a command group, eg. '
        '`{{pre}}help`, `{{pre}}help about` or `{{pre}}help Meta` '
        '\n__Understanding command usage:__\n'
        '`[value]`: optional value\n'
        '`<value>`: required value\n'
        '`[value...]` or `[value]...`: multiple values\n'
        '`[value="default"]`: default value available.'
        '\n__Values:__\n'
        'A value can be anything without a space in it, eg. `text`, '
        '`@user`, `#channel`, `3`, `no`. If you want text with a space '
        'in it, do `"some text"`.'
    )

    def get_command_signature(
            self, command: commands.Command,
            ignore_aliases: bool = False) -> str:
        """Get a command signature, but optionally ignore aliases."""
        if command.aliases and not ignore_aliases:
            aliases = '|'.join(command.aliases)
            name = f'[{command.name}|{aliases}]'
        else:
            name = command.name
        if command.parent:
            name = f'{command.full_parent_name} {name}'
        return f'{self.clean_prefix}{name} {command.signature}'

    async def send_bot_help(self, cogs: typing.Dict[
            commands.Cog, typing.Iterable[
                commands.Command
            ]], description: str = '', title: str = 'Help'):
        """Send help for the entire bot."""
        self.context.help_command_check = True
        e = discord.Embed(
            title=title, color=0x50C878, description=description
        )
        for cog in cogs:
            if not cog:
                continue
            lines = []
            for command in await self.filter_commands(cog.walk_commands()):
                if command.hidden:
                    continue
                signature = self.get_command_signature(
                    command, ignore_aliases=True
                )
                brief = command.brief or Help.brief
                line = f'**{signature}** *{brief}*'
                if line not in lines:     # Known bug where commands with
                    lines.append(line)    # aliases are duplicated.
            text = '\n'.join(lines)
            if text:
                e.add_field(name=cog.qualified_name, value=text, inline=False)
        await self.get_destination().send(embed=e)

    async def send_command_help(self, command: commands.Command):
        """Send help for a specific command."""
        if command.name == 'help':
            desc = Help.help
        else:
            desc = command.help
        desc = desc.replace('{{pre}}', self.context.prefix)
        title = self.get_command_signature(command)
        e = discord.Embed(title=title, color=0x50C878, description=desc)
        await self.get_destination().send(embed=e)

    async def send_cog_help(self, cog: commands.Cog):
        """Send help for a specific cog."""
        await self.send_bot_help({cog: cog.walk_commands()})

    async def send_group_help(self, group: commands.Group):
        """Send help for a command group."""
        await self.send_bot_help(
            {group: group.commands},
            description=group.help.replace('{{pre}}', self.context.prefix),
            title=self.get_command_signature(group)
        )
