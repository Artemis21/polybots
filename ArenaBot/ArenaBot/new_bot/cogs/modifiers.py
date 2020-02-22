from models.modifiers import Modifiers as Data
from discord.ext import commands


class Modifiers(commands.Cog):
    '''Commands for managing modifiers.
    '''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Get all modifiers.')
    async def modifiers(self, ctx):
        '''Get a list of all modifiers.
        '''
        for mes in Data.all():
            await ctx.send(mes)

    @commands.command(brief='Add a modifier.')
    @commands.has_permissions(manage_channels=True)
    async def addmod(ctx, name, turns: int, *, desc):
        '''Add a new modifier. May only be used by arena admins. A value of 0 \
        for turns means infinity. Examples:
        `mod new "Modifier Name" 0 The modifier description.`
        `mod new OneWordName 3 This modifier lasts for 3 turns.`
        '''
        Data.add(name, desc, turns)
        await ctx.send('Done!')

    @commands.command(brief='Edit a modifier.')
    @commands.has_permissions(manage_channels=True)
    async def editmod(ctx, num: int, field, *, new):
        '''Edit a modifier by number. Example:
        `mod edit 3 name New Modifier Name`
        `mod edit 4 desc The new modifier description.`
        `mod edit 8 turns 0`
        See numbers with the `mod all` command. `field` must be `name`, \
        `desc` or turns`.
        '''
        if num < 1:
            return await ctx.send('Modifier numbers are all positive...')
        if field not in ('name', 'desc', 'turns'):
            return await ctx.send(
                '`field` must be `name`, `desc` or `turns`. Do `mod help edit` '
                'for more info.'
            )
        try:
            Data.edit(num, field, new)
        except IndexError:
            return await ctx.send('Modifier not found.')
        await ctx.send('Done!')

    @commands.command(brief='Remove a modifier.')
    @commands.has_permissions(manage_channels=True)
    async def delmod(ctx, num: int):
        '''Remove a modifier by number.
        `mod del 3`
        '''
        if num < 1:
            return await ctx.send('Modifier numbers are all positive...')
        try:
            Data.rem(num)
        except IndexError:
            return await ctx.send('Modifier not found.')
        await ctx.send('Done!')
        
    
