from main.gamename import game
from main.cityname import city, alphabet
from discord.ext import commands


class Names(commands.Cog):
    '''Generate names for cities and games. Copies original game logic.
    '''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Get a city name.')
    async def city(self, ctx, tribe=''):
        '''Generate a city name. You may provide a tribe to search for. If no \
        tribe is provided, a random one will be chosen.
        Examples:
        `{{pre}}city` --> a random city name
        `{{pre}}city lux` --> a luxidoor city name
        '''
        await ctx.send(city(tribe))

    @commands.command(brief='Get a game name.')
    async def game(self, ctx, crazy: bool=False):
        '''Generate a game name. Set crazy to true for crazy game names. As \
        per the game, setting crazy to true does bot *guaruntee* craziness, \
        only gives a possibilty.
        Exampels:
        `{{pre}}game` --> generate a normal game name
        `{{pre}}game true` --> generate a crazy game name
        '''
        await ctx.send(game(crazy))

    @commands.command(breif='Get an alphabet.')
    async def letters(self, ctx, tribe=''):
        '''Get a tribe's alphabet. You may provide a tribe to search for. If \
        no tribe is provided, a random one will be chosen.
        Examples:
        `{{pre}}letters` --> a tribe's alphabet
        `{{pre}}letters lux` --> the luxidoorian alphabet
        '''
        await ctx.send(alphabet(tribe))
