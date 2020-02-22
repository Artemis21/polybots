from models.config import Config


async def announce(content='', embed=None):
    ch = Config.announce
    ping = Config.notify.mention
    await ch.send(content=ping + '\n' + content, embed=embed)
