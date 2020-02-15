from utils.colours import colours
import random
import discord


class Paginator:
    def __init__(self, ctx, maxpage):
        self.ctx = ctx
        self.pos = 0
        self.maxpage = maxpage
        self.mes = None
        ctx.bot.add_listener(self.on_reaction_add)

    async def setup(self):
        self.mes = await self.send(self.ctx.channel)
        await self.mes.add_reaction('◀')
        await self.mes.add_reaction('▶')

    async def send(self, channel):
        '''
        Send page number 1 to channel `channel` and return the message.
        '''
        raise(NotImplementedError('Send function must be implemented.'))

    async def edit(self, mes, page):
        '''
        Edit message `mes` to show page number `page`.
        '''
        raise(NotImplementedError('Edit function must be implemented.'))

    def back(self):
        if self.pos == 0:
            return
        self.pos -= 1

    def next(self):
        if self.pos == self.maxpage:
            return
        self.pos += 1

    async def on_reaction_add(self, react, user):
        if user != self.ctx.author:
            return
        if react.message.id != self.mes.id:
            return
        if react.emoji == '▶':
            self.next()
        elif react.emoji == '◀':
            self.back()
        await self.edit(self.mes, self.pos)
        await react.remove(user)


class FieldPaginator(Paginator):
    def __init__(self, ctx, title, fields, desc='', colour=None, maxf=10):
        if not colour:
            colour = random.choice(tuple(colours.values()))
        self.base = discord.Embed(title=title, desc=desc, color=colour)
        self.sets = [{}]
        for name, val in fields.items():
            if len(self.sets[-1]) >= maxf:
                self.sets.append({})
            self.sets[-1][name] = val
        super().__init__(ctx, len(self.sets) - 1)

    async def send(self, ch):
        e = self.base.copy()
        for name, val in self.sets[0].items():
            e.add_field(name=name, value=val, inline=False)
        e.set_footer(text=f'Page 1 of {len(self.sets)}.')
        return await ch.send(embed=e)

    async def edit(self, mes, page):
        e = self.base.copy()
        for name, val in self.sets[page].items():
            e.add_field(name=name, value=val, inline=False)
        e.set_footer(text=f'Page {page + 1} of {len(self.sets)}.')
        await mes.edit(embed=e)


class DescPaginator(Paginator):
    def __init__(self, ctx, title, desc, colour=None, maxlines=40,
                 pre='', end=''):
        if not colour:
            colour = random.choice(tuple(colours.values()))
        self.base = discord.Embed(title=title, desc=desc, color=colour)
        sets = ['']
        for line in desc.split('\n'):
            if len(sets[-1].split('\n')) == maxlines:
                sets.append('')
            sets[-1] += '\n' + line
        self.sets = [pre + i + end for i in sets]
        super().__init__(ctx, len(self.sets) - 1)

    async def send(self, ch):
        e = self.base.copy()
        e.description = self.sets[0] or '<none>'
        e.set_footer(text=f'Page 1 of {len(self.sets)}.')
        return await ch.send(embed=e)

    async def edit(self, mes, page):
        e = self.base.copy()
        e.description = self.sets[page] or '<none>'
        e.set_footer(text=f'Page {page + 1} of {len(self.sets)}.')
        await mes.edit(embed=e)
