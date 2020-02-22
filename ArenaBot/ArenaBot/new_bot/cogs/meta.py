from discord.ext import commands, tasks
from models.config import Config
import discord
import os
from utils.colours import colours
from utils.paginator import FieldPaginator as Paginator


AUTHOR = 'Artemis#8032'
OTHER = (
    'ArenaBot is a bot dedicated to helping out with running the arena in '
    'the Polytopia Luxidor server, "The Grand Palace of Luxidoor". Have fun, '
    'and check out <#625005225102671892>!'
)
INVITE = (
    'https://discordapp.com/api/oauth2/authorize?client_id={}&permissions=8'
    '&scope=bot'
)


class Help(commands.DefaultHelpCommand):
    brief = 'Shows this message.'
    description = (
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
        'in it, do `"some text"`. Yes/no values can be any of '
        '`yes`, `y`, `true`, `t`, `1`, `enable` or `on` for yes, or '
        '`no`, `n`, `false`, `f`, `0`, `disable` or `off` for no.\n\n'
    )

    def get_embed(self, desc=''):
        embed = discord.Embed(color=colours['green'], description=desc)
        embed.set_author(name='Help', icon_url=bot.user.avatar_url)
        return embed

    def get_cog(self, cog, coms):
        if not cog:
            return
        value = ''
        part = 1
        ret = {}
        for i in coms:
            if i.hidden:
                continue
            new = ('**' + self.get_command_signature(i) + '**   *'
                   + (i.brief or Help.brief) + '*\n')
            if (len(value) + len(new)) > 1024:
                ret[cog.qualified_name + f'(part {part})\n'] = value
                value = new
                part += 1
            else:
                value += new
        name = cog.qualified_name
        if part != 1:
            name += f'(part {part})'
        ret[name + '\n'] = value
        return ret

    async def send_bot_help(self, cogs):
        fields = {}
        for i in cogs:
            new = self.get_cog(i, cogs[i])
            if new:
                fields.update(new)
        pag = Paginator(
            self.context, 'Help', fields, colour=colours['green'], maxf=3
        )
        await pag.setup()

    async def send_command_help(self, command):
        embed = self.get_embed()
        desc = command.help or command.description or Help.description
        desc = desc.replace('{{pre}}', self.context.prefix)
        embed.add_field(name=self.get_command_signature(command),
                        value=desc)
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        desc = cog.description.replace('{{pre}}', self.context.prefix)
        embed = self.get_embed(desc=desc)
        coms = await self.filter_commands(cog.get_commands())
        for name, val in self.get_cog(cog, coms).items():
            embed.add_field(name=name, value=val)
        await self.get_destination().send(embed=embed)


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.command_prefix = Config.get_prefix
        helpcom = Help()
        bot.help_command = helpcom
        helpcom.cog = self

    @commands.Cog.listener()
    async def on_message(self, mes):
        if self.bot.user in mes.mentions:
            pre = self.bot.command_prefix
            if type(pre) != str:
                pre = pre(self.bot, mes)
            await mes.channel.send(f'My prefix is `{pre}`.')

    @commands.command(brief='Info on the bot.')
    async def about(self, ctx):
        '''Find out a little more about the bot.
        '''
        embed = discord.Embed(
            color=colours['purple'], description=OTHER, title='About'
        )
        embed.set_thumbnail(url=bot.user.avatar_url)
        embed.add_field(name='Author', value=AUTHOR)
        embed.add_field(
            name='Invite',
            value=f'**[Click Here]({INVITE.format(bot.user.id)})**'
        )
        await ctx.send(embed=embed)

    @commands.command(brief='Stats about the bot')
    async def stats(self, ctx):
        '''Various statistics about the bot, such as server count, member \
        count and ping time.
        '''
        embed = discord.Embed(color=colours['lightblue'], title='Statistics')
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(
            name='Shard',
            value=f'#{self.bot.shard_id or 1} of {self.bot.shard_count or 1}'
        )
        embed.add_field(
            name='Discord API ping',
            value=f'{str(self.bot.latency * 1000)[:3]}ms'
        )
        embed.add_field(name='Guilds', value=len(self.bot.guilds))
        embed.add_field(name='Users', value=len(self.bot.users))
        await ctx.send(embed=embed)

    @commands.command(brief='See the guilds.', hidden=True)
    @commands.is_owner()
    async def snoop(self, ctx):
        '''See servers with their counts and invites.
        '''
        rows = []
        for i in self.bot.guilds:
            line = f'{i.name} | {len(i.members)}'
            try:
                invs = await i.invites()
                line = invs[0].url
            except Exception:
                pass
            rows.append(line)
        await ctx.send('\n'.join(rows))

    @commands.command(brief='Backup ./data', hidden=True)
    @commands.is_owner()
    async def backup(self, ctx, n: int):
        ''''Move a copy of `./data` to `../backup/botdata/{n}/`'
        '''
        if os.system(f'mkdir ../backup/botdata/{n}') == 256:
            os.system('mkdir ../backup')
            os.system('mkdir ../backup/botdata')
            os.system(f'mkdir ../backup/botdata/{n}')
        c = os.system(f'cp data ../backup/botdata/{n} -r')
        await ctx.send(f'Backup completed with exit code {c}.')
