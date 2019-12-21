import json


with open('config/settings.json') as f:
    data = json.load(f)


def load(bot):
    usr = bot.get_user(data['ramana'])
    RAMANA = usr.dm_channel
    if not ch:
        await usr.create_dm()
        RAMANA = usr.dm_channel
    ANNOUNCE = bot.get_channel(data['announce'])
