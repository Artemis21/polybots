import discord
from discord.ext import commands
import logging
import re
import traceback
import random
import sqlite3
import string



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

COLOURS = {
    'bad': 0xFF0066,
    'good': 0x00FF66,
    'neutral': 0x0066FF,
}

db = sqlite3.connect('db.sqlite3')


def sql(command, *params):
    cur = db.cursor()
    cur.execute(command, params)
    res = cur.fetchall()
    db.commit()
    return res


def ensure_tables():
    sql("""CREATE TABLE IF NOT EXISTS channels (
        channel INTEGER, user INTEGER
    );""")
    sql("""CREATE TABLE IF NOT EXISTS archives (
        category INTEGER, name STRING
    );""")
    sql("""CREATE TABLE IF NOT EXISTS users (
        user INTEGER, code STRING, tz STRING
    );""")


def add_channel(channel, user):
    sql(
        'INSERT INTO channels (channel, user) VALUES (?, ?);',
        channel.id, user.id
    )


def get_owner(channel):
    rows = sql('SELECT user FROM channels WHERE channel=?;', channel.id)
    if rows:
        return bot.get_user(rows[0][0])


def add_archive(category, name):
    sql(
        'INSERT INTO archives (category, name) VALUES (?, ?);',
        category.id, name.lower()
    )


def delete_archive(name):
    sql('DELETE FROM archives WHERE name=?;', name.lower())


def get_archive(name):
    rows = sql('SELECT category FROM archives WHERE name=?;', name.lower())
    if rows:
        return bot.get_channel(rows[0][0])


def get_archives():
    rows = sql('SELECT category, name FROM archives;')
    for row in rows:
        yield bot.get_channel(row[0]), row[1].lower()


def get_user_attr(user, attr):
    rows = sql(f'SELECT {attr} FROM users WHERE user=?;', user)
    if rows:
        return rows[0][0]


def set_user_attr(user, attr, value):
    if sql('SELECT * FROM users WHERE user=?;', user):
        sql(f'UPDATE users SET {attr}=? WHERE user=?;', value, user)
    else:
        sql(f'INSERT INTO users (user, {attr}) VALUES (?, ?);', user, value)


def migrate_users():
    exists = sql(
        'SELECT name FROM sqlite_master WHERE '
        f'type="table" AND name="codes";'
    )
    if exists:
        rows = sql('SELECT user, code FROM codes;')
        for row in rows:
            sql('INSERT INTO users (user, code) VALUES (?, ?);', *row)
        sql('DROP TABLE codes;')


class CategoryConverter(commands.converter.CategoryChannelConverter):
    def make_plain(self, name):
        """Make a name lowercase and remove all non-letter, non-number
        characters for easy comparison.
        """
        plain = ''
        for char in name:
            if char in string.ascii_letters + string.digits:
                plain += char.lower()
        return plain

    async def convert(self, ctx, argument):
        try:
            return await super().convert(ctx, argument)
        except commands.BadArgument as error:
            # have an extra try at converting it
            plain_argument = self.make_plain(argument)
            if ctx.guild:
                for category in ctx.guild.categories:
                    if self.make_plain(category.name) == plain_argument:
                        return category
            # if we still can't, raise the original error
            raise error


class Help(commands.DefaultHelpCommand):
    brief = 'Shows this message.'
    help = 'Provides help on a command.'

    async def send_bot_help(self, cogs):
        lines = []
        for cog in cogs:
            for command in cogs[cog]:
                line = '**{}** *{}*'.format(
                    self.get_command_signature(command),
                    command.brief or Help.brief
                )
                if line not in lines:
                    lines.append(line)
        e = discord.Embed(
            title='Help', colour=COLOURS['good'], description='\n'.join(lines)
        )
        await self.get_destination().send(embed=e)

    async def send_command_help(self, command):
        desc = (command.help or Help.help).replace(
            '{{pre}}', bot.command_prefix
        )
        title = self.get_command_signature(command)
        e = discord.Embed(
            title=title, colour=COLOURS['good'], description=desc
        )
        await self.get_destination().send(embed=e)

    async def send_cog_help(self, cog):
        await self.send_bot_help(bot.cogs)


logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix='?')
bot.help_command = Help()


@bot.event
async def on_ready():
    ensure_tables()
    migrate_users()


@bot.event
async def on_command_error(ctx, error):
    rawtitle = type(error).__name__
    rawtitle = re.sub('([a-z])([A-Z])', r'\1 \2', rawtitle)
    title = rawtitle[0].upper() + rawtitle[1:].lower()
    e = discord.Embed(
        colour=COLOURS['bad'], title=title, description=str(error)
    )
    await ctx.send(embed=e)
    if hasattr(error, 'original'):
        err = error.original
        traceback.print_tb(err.__traceback__)
        print(f'{type(err).__name__}: {err}.')


@bot.command(brief='About the bot.')
async def about(ctx):
    """Provides some details relating to the bot."""
    e = discord.Embed(
        colour=COLOURS['neutral'], title='About', description=DESC
    )
    e.set_thumbnail(url=bot.user.avatar_url)
    e.set_footer(text=ADVERT, icon_url=AD_ICON)
    await ctx.send(embed=e)


@bot.command(brief='Flip a coin.')
async def flip(ctx):
    """Flip a coin, returns either heads or tails."""
    await ctx.send(random.choice(('Heads', 'Tails')))


@bot.command(brief='Get a friend code.')
async def code(ctx, *, user: discord.Member):
    """Get someone's friend code."""
    code = get_user_attr(user.id, 'code')
    if code:
        await ctx.send(f'`{code}`')
    else:
        await ctx.send(f'{user} has not set a code.')


@bot.command(brief='Set your friend code.', name='set-code', aliases=['setcode'])
async def set_code_cmd(ctx, code):
    """Set your friend code."""
    set_user_attr(ctx.author.id, 'code', code)
    await ctx.send('Done!')


@bot.command(brief='Get a timezone.')
async def tz(ctx, *, user: discord.Member):
    """Get someone's timezone."""
    tz = get_user_attr(user.id, 'tz')
    if tz:
        await ctx.send(f'`{tz}`')
    else:
        await ctx.send(f'{user} has not set a timezone.')


@bot.command(brief='Set your timezone.', name='set-tz')
async def set_tz_cmd(ctx, tz):
    """Set your timezone."""
    set_user_attr(ctx.author.id, 'tz', tz)
    await ctx.send('Done!')


@bot.command(brief='Unlock this channel.')
async def unlock(ctx):
    """Unlock the channel this command is sent in.

    Requires that you own this channel or you are an admin.
    You should only run this at the end of a game.
    """
    allowed = getattr(get_owner(ctx.channel), 'id', None) == ctx.author.id
    if not allowed:
        allowed = ctx.channel.permissions_for(ctx.author).manage_channels
    if not allowed:
        return await ctx.send(
            'Only the owner of this channel (or an admin) may unlock it.\n'
            'Note: only admins may unlock games created before the 28th of '
            'April due to technical issues.'
        )
    overwrites = {}
    for target in ctx.channel.overwrites:
        overwrites[target] = discord.PermissionOverwrite()
    await ctx.channel.edit(overwrites=overwrites)
    await ctx.send('Done!')


@bot.command(brief='Re-lock this channel.')
async def relock(ctx):
    """Re-lock the channel this command is sent in.

    Requires that you own this channel or you are an admin.
    This is for when you accidentally do `{{pre}}unlock`.
    """
    owner_id = getattr(get_owner(ctx.channel), 'id', None)
    allowed = owner_id == ctx.author.id
    if not allowed:
        allowed = ctx.channel.permissions_for(ctx.author).manage_channels
    if not allowed:
        return await ctx.send(
            'Only the owner of this channel (or an admin) may unlock it.\n'
            'Note: only admins may unlock games created before the 28th of '
            'April due to technical issues.'
        )
    overwrites = {}
    for other_channel in ctx.channel.category.channels:
        opponent = get_owner(other_channel)
        if opponent and opponent.id != owner_id:
            overwrites[opponent] = discord.PermissionOverwrite(
                read_messages=False
            )
    await ctx.channel.edit(overwrites=overwrites)
    await ctx.send('Done!')


@bot.command(brief='Create a game.')
@commands.has_permissions(manage_channels=True)
async def game(
        ctx, player1: discord.Member, player2: discord.Member, *, label=''
        ):
    """Create a set of game channels.
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
    """
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
        add_channel(c, player)
        await c.send(player.mention)
    await disc.send(' '.join(i.mention for i in players))
    await ctx.send(f'Done! ({disc.mention})')


@bot.command(brief='Archive this category.')
@commands.has_permissions(manage_channels=True)
async def archive(ctx, *, archive_name):
    """Archive the channel category this command is used in. This will delete \
    the discussion channel and category, and move the channels in it to the \
    archive category you select. Add archive categories to the bot with the \
    `{{pre}}addarchive` command.
    Example:
    `{{pre}}archive tourney`: archive this game to the archive called tourney.
    NOTE: you must run this command in the discussion channel of a game.
    """
    if str(ctx.channel) != 'discussion' or not ctx.channel.category_id:
        return await ctx.send(
            'This command must be run in a discussion channel.'
        )
    archive = get_archive(archive_name)
    if not archive:
        return await ctx.send(f'No archive named `{archive_name}`.')
    if len(archive.channels) > 48:
        return await ctx.send(
            f'The category {archive} is full, categories may only contain 50 '
            'channels.'
        )
    category = bot.get_channel(ctx.channel.category_id)
    unlocked = discord.PermissionOverwrite()
    for channel in category.channels:
        if channel.id != ctx.channel.id:
            perms = {}
            for target in channel.overwrites:
                perms[target] = unlocked
            await channel.edit(category=archive, overwrites=perms)
            await channel.send(f'{ctx.author.mention} archived!')
    await ctx.channel.delete()
    await category.delete()


@bot.command(brief='Add an archive.', name='add-archive')
@commands.has_permissions(manage_channels=True)
async def add_archive_cmd(ctx, name, *, category: CategoryConverter):
    """Add an archive category.
    
    Examples:
    `{{pre}}add-archive tourney TOURNEY ARCHIVES`: add the TOURNEY ARCHIVES \
    category as an archive called `tourney`.
    `{{pre}}add-archive main2 704745698729525321`: add an archive called \
    `main2` by category ID.
    """
    if get_archive(name):
        return await ctx.send(
            'There is already an archive by that name, please delete it or '
            'use another name.'
        )
    add_archive(category, name)
    await ctx.send('Done!')


@bot.command(brief='View archives.')
async def archives(ctx):
    """View a list of archive categories."""
    raw = get_archives()
    lines = []
    for category, name in raw:
        lines.append(f'**{category.name.upper()}** (*{name}*)')
    main = '\n'.join(lines) or '*No archives.*'
    await ctx.send(embed=discord.Embed(
        title='Archives', description=main, colour=COLOURS['neutral']
    ))


@bot.command(brief='Delete an archive.', name='delete-archive')
async def delete_archive_cmd(ctx, *, name):
    """Delete an archive category from the bot. This will not delete the \
    category in discord.

    Example:
    `{{pre}}delete-archive tourney`: delete the archive called `tourney`.
    """
    if not get_archive(name):
        return await ctx.send(f'No archive named `{name}`.')
    delete_archive(name)
    await ctx.send('Archive deleted.')


# https://discordapp.com/api/oauth2/authorize?client_id=694291738264862782&permissions=388177&scope=bot
bot.run(TOKEN)
