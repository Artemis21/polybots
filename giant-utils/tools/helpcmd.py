"""Discord.py help command."""
import typing

import discord
from discord.ext import commands

from tools import colours


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

    async def send_bot_help(self, cogs: typing.Dict[
            commands.Cog, typing.Iterable[
                commands.Command
            ]]):
        """Send help for the entire bot."""
        e = discord.Embed(title='Help', color=colours.HELP)
        for cog in cogs:
            if not cog:
                continue
            lines = []
            for command in cogs[cog]:
                if command.hidden:
                    continue
                line = '**{cmd}** *{brief}*'.format(
                    cmd=self.get_command_signature(command),
                    brief=command.brief or Help.brief
                )
                if line not in lines:     # known bug where commands with
                    lines.append(line)    # aliases are duplicated
            text = '\n'.join(lines)
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
        e = discord.Embed(title=title, color=colours.HELP, description=desc)
        await self.get_destination().send(embed=e)

    async def send_cog_help(self, cog: commands.Cog):
        """Send help for a specific cog."""
        await self.send_bot_help({cog: cog.walk_commands()})
