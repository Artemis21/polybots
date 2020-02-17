import json
from discord.ext import commands
import discord
import random


class Modifiers:
    @classmethod
    def load(cls):
        try:
            with open('mods.json') as f:
                raw = json.load(f)
        except FileNotFoundError:
            raw = {}
        cls.mods = raw.get('mods', [])

    @classmethod
    def tostr(cls, mod):
        name = mod['name']
        desc = mod['desc']
        turns = mod['turns'] or '∞'
        return f'**{name}**: {desc} *(lasts {turns} turns in scramble games)*'

    @classmethod
    def get(cls):
        mods = cls.mods or ['No modifiers found.']
        mod = random.choice(mods)
        return cls.tostr(mod)

    @classmethod
    def all(cls):
        n = 1
        t = 'All modifiers:'
        for mod in cls.mods:
            t += f'\n**({n})** {cls.tostr(mod)}'
            n += 1
        return t

    @classmethod
    def add(cls, name, desc, turns):
        cls.mods.append({
            'name': name,
            'desc': desc,
            'turns': turns,
        })
        cls.save()

    @classmethod
    def rem(cls, num):
        del cls.mods[num - 1]
        cls.save()

    @classmethod
    def edit(cls, num, field, new):
        cls.mods[num-1][field] = new
        cls.save()

    @classmethod
    def save(cls):
        data = {'mods': cls.mods}
        with open('mods.json', 'w') as f:
            json.dump(data, f)


def admins():
    async def predicate(ctx):
        return ctx.author.id in [
            610146313463660565,  # Rook
            588943380835336203,  # Mik Mik
            496381034628251688,  # Artemis
        ]
    return commands.check(predicate)


bot = commands.Bot(command_prefix=('mod ', 'Mod '))
Modifiers.load()


@bot.event
async def on_ready():
    print('Ready!')
    

@bot.command(brief='Get a modifier.')
async def get(ctx):
    '''Get a random modifier.
    '''
    await ctx.send(Modifiers.get())


@bot.command(brief='See all modifiers.', name='all')
async def all_(ctx):
    '''Get a list of every modifier.
    '''
    await ctx.send(Modifiers.all())


@bot.command(brief='Add a new modifier.')
@admins()
async def new(ctx, name, turns: int, *, desc):
    '''Add a new modifier. May only be used by arena admins. A value of 0 for \
    turns means infinity. Examples:
    `mod new "Modifier Name" 0 The modifier description.`
    `mod new OneWordName 3 This modifier lasts for 3 turns.`
    '''
    Modifiers.add(name, desc, turns)
    await ctx.send('Done!')


@bot.command(brief='Edit a modifier.', name='edit')
@admins()
async def edit(ctx, num: int, field, *, new):
    '''Edit a modifier by number. May only be used by arena admins. Example:
    `mod edit 3 name New Modifier Name`
    `mod edit 4 desc The new modifier description.`
    `mod edit 8 turns 0`
    See numbers with the `mod all` command. `field` must be `name`, `desc` or \
    `turns`.
    '''
    if num < 1:
        return await ctx.send('Modifier numbers are all positive...')
    if field not in ('name', 'desc', 'turns'):
        return await ctx.send(
            '`field` must be `name`, `desc` or `turns`. Do `mod help edit` '
            'for more info.'
        )
    try:
        Modifiers.edit(num, field, new)
    except IndexError:
        return await ctx.send('Modifier not found.')
    await ctx.send('Done!')


@bot.command(brief='Remove a modifier.', name='del')
@admins()
async def del_(ctx, num: int):
    '''Remove a modifier by number. May only be used by arena admins. Example:
    `mod del 3`
    See numbers with the `mod all` command.
    '''
    if num < 1:
        return await ctx.send('Modifier numbers are all positive...')
    try:
        Modifiers.rem(num)
    except IndexError:
        return await ctx.send('Modifier not found.')
    await ctx.send('Done!')


with open('TOKEN') as f:
    bot.run(f.read().strip())
