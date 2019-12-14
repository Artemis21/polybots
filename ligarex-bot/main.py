import discord


cl = discord.Client()


NON_TEAM_ROLES = (
    627379287258955777,   #Rex
    625824571152662538,   #Bot Shepard
    625824429531987999    #LigaRex
)



@cl.event
async def on_guild_channel_create(ch):
    def check(m):
        return m.channel.id == ch.id and m.author.id == 484067640302764042
    mes = await cl.wait_for('message', check=check)
    roles = mes.mentions[0].roles
    for i in roles:
        if i.id not in NON_TEAM_ROLES and i != ch.guild.default_role:
            role = i
            break
    await ch.set_permissions(role, reason='Team', read_messages=True, send_messages=True)
    await ch.send('Done perms!')


@cl.event
async def on_message(mes):
    if cl.user in mes.mentions:
        await mes.channel.send('Fully operational!')


@cl.event
async def on_ready():
    print('Ready!')


with open('TOKEN') as f:
    token = f.read().strip()

cl.run(token)
