import json
from discord.ext import commands


with open('config/settings.json') as f:
    data = json.load(f)


def admin(user):
    return user.id in data['admins']


def channel(ctx):
    if ctx.channel.id in data['channels']:
        return True
    raise commands.NoPrivateMessage(
        'This bot may only used in whitelisted TT1 channels.'
    )


async def caution(ctx, bot):
    await ctx.send(
        'Are you sure you wish to procede? This cannot be undone. `Yes` to'
        ' continue, anything else to cancel.'
    )

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    mes = await bot.wait_for('message', check=check)
    if mes.content.upper() != 'YES':
        await ctx.send('Cancelled.')
        return False
    return True
