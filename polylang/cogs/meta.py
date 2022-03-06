import discord.ext.commands as commands
import discord
import os
from utils.colours import colours
from utils.paginator import FieldPaginator as Paginator
import json


AUTHOR = '[Artemis](https://arty.li)'
OTHER = (
    'PolyLang is a Discord bot made to generate words and phrases in the '
    'languages of Polytopia.'
)
INVITE = (
    'https://discordapp.com/api/oauth2/authorize?client_id={}&permissions=8'
    '&scope=bot'
)
SOURCE = 'https://github.com/Artemis21/Polybots'


class Help(commands.DefaultHelpCommand):
    brief = 'Shows this message.'
    help = 'Provides help on a command.'

    async def send_bot_help(self, cogs):
        text = ''
        for cog in cogs:
            for command in cogs[cog]:
                if command.hidden:
                    continue
                text += '**{}** *{}*\n'.format(
                    self.get_command_signature(command),
                    command.brief or Help.brief
                )
        e = discord.Embed(title='Help', color=0x00FF66, description=text)
        await self.get_destination().send(embed=e)

    async def send_command_help(self, command):
        desc = (command.help or Help.help).replace(
            '{{pre}}', bot.command_prefix
        )
        title = self.get_command_signature(command)
        e = discord.Embed(title=title, color=0x00FF66, description=desc)
        await self.get_destination().send(embed=e)

    async def send_cog_help(self, cog):
        await self.send_bot_help(bot.cogs)


class Meta(commands.Cog):
    '''
    Commands related to the bot itself.
    '''
    def __init__(self, bot_):
        global bot
        bot = bot_
        bot.help_command = Help()

    @commands.Cog.listener()
    async def on_message(self, mes):
        if bot.user in mes.mentions:
            pre = bot.command_prefix
            await mes.channel.send(f'My prefix is `{pre}`.')

    @commands.command(
        brief='Info on the bot.',
        description='Find out a little more about the bot.'
    )
    async def about(self, ctx):
        embed = discord.Embed(
            color=colours['purple'], description=OTHER, title='About'
        )
        embed.set_thumbnail(url=str(bot.user.avatar))
        embed.add_field(name='Author', value=AUTHOR)
        embed.add_field(
            name='Invite',
            value=f'**[Click Here]({INVITE.format(bot.user.id)})**'
        )
        embed.add_field(
            name='Source code',
            value=f'**[Click Here]({SOURCE.format(bot.user.id)})**'
        )
        await ctx.send(embed=embed)

    @commands.command(
        brief='Stats about the bot',
        description=(
            'Various statistics about the bot, such as server count, member '
            'count and ping time.'
        )
    )
    async def stats(self, ctx):
        embed = discord.Embed(color=colours['lightblue'], title='Statistics')
        embed.set_thumbnail(url=str(bot.user.avatar))
        embed.add_field(
            name='Shard',
            value=f'#{bot.shard_id or 1} of {bot.shard_count or 1}'
        )
        embed.add_field(
            name='Discord API ping', value=f'{str(bot.latency * 1000)[:3]}ms'
        )
        embed.add_field(name='Guilds', value=len(bot.guilds))
        embed.add_field(name='Users', value=len(bot.users))
        await ctx.send(embed=embed)

    @commands.command(
        brief='See the guilds.',
        description='See servers with their counts and invites.',
        hidden=True
    )
    @commands.is_owner()
    async def snoop(self, ctx):
        rows = []
        for i in bot.guilds:
            line = f'{i.name} | {len(i.members)}'
            try:
                invs = await i.invites()
                line = invs[0].url
            except Exception:
                pass
            rows.append(line)
        await ctx.send('\n'.join(rows))
