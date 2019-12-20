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
