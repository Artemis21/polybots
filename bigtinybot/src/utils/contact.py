import json


with open('config/settings.json') as f:
    data = json.load(f)


async def load(bot):
    global RAMANA, ANNOUNCE
    usr = bot.get_user(data['ramana'])
    RAMANA = usr.dm_channel
    if not RAMANA:
        await usr.create_dm()
        RAMANA = usr.dm_channel
    ANNOUNCE = bot.get_channel(data['announce'])
