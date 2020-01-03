import json
import re
from discord.ext import commands, tasks
import discord
from utils.colours import colours


class Users:
    default = {
        'Timezone': 'Unknown',
        'Friend Code': 'Unknown',
        'In-game Name': 'Unknown',
        'Points': 0,
        'Tier': 1,
    }
    fields = {
        'Timezone': 'UTC[+-][0-9]{2}',
        'Friend Code': '[a-zA-Z0-9]{16}',
        'In-game Name': '[^\n]{1,30}',
    }

    @classmethod
    async def load(cls):
        with open('data/users.json') as f:
            cls.data = json.load(f)
        cls.save.start()

    @classmethod
    @tasks.loop(minutes=1)
    async def save(cls=None):
        cls = cls or Users    # loop doesn't seem to work with classmethod
        with open('data/users.json', 'w') as f:
            json.dump(cls.data, f)

    @classmethod
    def get_data(cls, uid):
        return cls.data.get(str(uid), cls.default)

    @classmethod
    def set_data(cls, uid, data, field):
        p = cls.fields[field] + '$'
        if not re.match(p, data):
            return 1, f'invalid value `{data}` provided for `{field}`'
        if str(uid) not in cls.data:
            cls.data[str(uid)] = cls.default
        cls.data[str(uid)][field] = data
        return 0, f'value for `{field}` set to `{data}`'
