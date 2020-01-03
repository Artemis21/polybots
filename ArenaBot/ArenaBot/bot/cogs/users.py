


class Details(commands.Cog):
    '''
    View and set user details:
     - timezone
     - in-game name
     - friend code
    '''
    def __init__(self, bot_):
        global bot
        bot = bot_
        self.ready = False

    @commands.Cog.listener()
    async def on_ready(self):
        if self.ready:
            return
        await Users.load()
        self.ready = True

    async def use_code(self, ctx, s, m):
        if s:
            await ctx.send(f'Error: {m}.')
        else:
            await ctx.send(f'Success: {m}.')

    @commands.command(
        brief='See a user\'s details.',
        description=(
            'See a user\'s in-game name, timezone and friend code. Use '
            '`{{pre}}code @user` to get the code sent in a seperate '
            'message for easier copying.'
        )
    )
    async def userinfo(self, ctx, user: discord.Member):
        data = Users.get_data(user.id)
        e = discord.Embed(title=str(user), colour=colours['green'])
        for field in data:
            e.add_field(name=field, value=data[field])
        await ctx.send(embed=e)

    @commands.command(
        brief='Copy a friend code.',
        description=(
            'Get a user\'s friend code sent in a seperate message for easy '
            'copying.'
        )
    )
    async def code(self, ctx, user: discord.Member):
        data = Users.get_data(user.id)
        name = data['In-game Name']
        await ctx.send(f'Friend code for {user} (in-game name: {name}):')
        await ctx.send(data['Friend Code'])

    @commands.command(
        brief='Set your timezone.',
        description=(
            'Set your timezone for others to know when you\'ll be online. '
            'Use the format `UTC±HH`, eg. `UTC+03` or `UTC-10`.'
        )
    )
    async def settz(self, ctx, timezone):
        s, m = Users.set_data(ctx.author.id, timezone, 'Timezone')
        await self.use_code(ctx, s, m)

    @commands.command(
        brief='Set your in-game name.',
        description=(
            'Set the name Polytopia uses for you, so others can recognize you '
            'more easily.'
        )
    )
    async def setname(self, ctx, name):
        s, m = Users.set_data(ctx.author.id, name, 'In-game Name')
        await self.use_code(ctx, s, m)

    @commands.command(
        brief='Set your friend code.',
        description=(
            'Set your Polytopia friend code so that others can add you to '
            'games.'
        )
    )
    async def setcode(self, ctx, code):
        s, m = Users.set_data(ctx.author.id, code, 'Friend Code')
        await self.use_code(ctx, s, m)
