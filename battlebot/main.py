import discord
from discord.ext import commands
import logging
import re
import traceback


with open('TOKEN') as f:
    TOKEN = f.read().strip()

DESC = (
    'BattleBot is a simple helper bot created by Artemis#8799 for the '
    'Battle Teachings server. It\'s current functions are creating and '
    'archiving game channels. The source code is available '
    '[here](https://github.com/Artemis21/polybots/tree/master/battlebot).'
)
ADVERT = 'Order a bot at artybot.xyz.'
AD_ICON = 'https://artybot.xyz/static/icon.png'

ARCHIVES = {
    'a': 692808476778430574,
    'archives': 692808476778430574,
    't': 696395537993170997,
    'tourney': 696395537993170997,
}


class Help(commands.DefaultHelpCommand):
    brief = 'Shows this message.'
    help = 'Provides help on a command.'

    async def send_bot_help(self, cogs):
        text = ''
        for cog in cogs:
            for command in cogs[cog]:
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
        await self.send_bot_help()


logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix='!')
bot.help_command = Help()


@bot.event
async def on_command_error(ctx, error):
    rawtitle = type(error).__name__
    rawtitle = re.sub('([a-z])([A-Z])', r'\1 \2', rawtitle)
    title = rawtitle[0].upper() + rawtitle[1:].lower()
    e = discord.Embed(color=0xFF0066, title=title, description=str(error))
    await ctx.send(embed=e)
    if hasattr(error, 'original'):
        err = error.original
        traceback.print_tb(err.__traceback__)
        print(f'{type(err).__name__}: {err}.')


@bot.command(brief='About the bot.')
async def about(ctx):
    '''Provides some details relating to the bot.
    '''
    e = discord.Embed(colour=0x0066FF, title='About', description=DESC)
    e.set_thumbnail(url=bot.user.avatar_url)
    e.set_footer(text=ADVERT, icon_url=AD_ICON)
    await ctx.send(embed=e)


@bot.command(brief='Create a game.')
@commands.has_permissions(manage_channels=True)
async def game(
        ctx, player1: discord.Member, player2: discord.Member, *, label=''
        ):
    '''Create a set of game channels.
    Examples:
    `{{pre}}game @player1 @player2` makes:
        PLAYER1 VS PLAYER2
        ├─ #discussion
        ├─ #player1
        └─ #player2
    `{{pre}}game @artemis @reality tourney` makes:
        TOURNEY ARTEMIS VS REALITY
        ├─ #discussion
        ├─ #artemis
        └─ #reality
    Each player will be locked out of the other player's channel. The \
    category will be placed at the end of the channel list. You must have the \
    manage channels permission to run this command.
    '''
    name = f'{label} {player1.name} vs {player2.name}'
    cat = await ctx.guild.create_category(name)
    disc = await cat.create_text_channel('discussion')
    players = (player1, player2)
    locked = discord.PermissionOverwrite(read_messages=False)
    for player in players:
        overwrites = {}
        for other in players:
            if other != player:
                overwrites[other] = locked
        c = await cat.create_text_channel(player.name, overwrites=overwrites)
        await c.send(player.mention)
    await disc.send(' '.join(i.mention for i in players))
    await ctx.send(f'Done! ({disc.mention})')


@bot.command(brief='Archive this category.')
@commands.has_permissions(manage_channels=True)
async def archive(ctx, archive='archives'):
    '''Archive the channel category this command is used in. This will delete \
    the discussion channel and category, and move the channels in it to the \
    archive channel. You can optionally specify a parameter which tells the \
    bot which archive to use. Default is "archives", which means the ARCHIVES \
    category, but you can also use "tourney" or "t", which means TOURNEY \
    ARCHIVES.
    Examples:
    `{{pre}}archive`: archive this game to the ARCHIVES category
    `{{pre}}archive t`: archive this game to the TOURNEY ARCHVIES category.
    NOTE: you must run this command in the discussion channel of a game.
    '''
    if str(ctx.channel) != 'discussion' or not ctx.channel.category_id:
        return await ctx.send(
            'This command must be run in a discussion channel.'
        )
    archive = archive.lower()
    if archive not in ARCHIVES:
        return await ctx.send(
            '`archive` must be one of "archives", "a", "tourney" or "t". Run '
            '`!help archive` for more info.'
        )
    archive = bot.get_channel(ARCHIVES[archive])
    if len(archive.channels) > 48:
        return await ctx.send(
            f'The category {archive} is full, categories may only contain 50 '
            'channels.'
        )
    category = bot.get_channel(ctx.channel.category_id)
    for channel in category.channels:
        if channel.id != ctx.channel.id:
            await channel.edit(category=category)
            await channel.send(f'{ctx.author.mention} archived!')
    await ctx.channel.delete()
    await category.delete()


# https://discordapp.com/api/oauth2/authorize?client_id=694291738264862782&permissions=388177&scope=bot
bot.run(TOKEN)
