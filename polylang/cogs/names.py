from main.gamename import game
from main.cityname import city, alphabet
from main.elyrion import ely_to_eng, eng_to_ely
from discord.ext import commands
import discord


async def imitate(ctx, text):
    try:
        whs = await ctx.channel.webhooks()
        if whs:
            wh = whs[0]
        else:
            wh = await ctx.channel.create_webhook(name='Toolkit')
        await wh.send(
            text, username=ctx.author.display_name, 
            avatar_url=str(ctx.author.avatar_url)
        )
    except discord.Forbidden:
        e = discord.Embed(description=text)
        e.set_author(
            name=ctx.author.display_name, 
            icon_url=str(ctx.author.avatar_url)
        )
        e.set_footer(
            text='For full fuctionality, please give the bot the manage webhooks '
                 'permission.'
        )
        await ctx.send(embed=e)
    await ctx.message.delete()


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

    @commands.command(brief='Get an alphabet.')
    async def letters(self, ctx, tribe=''):
        '''Get a tribe's alphabet. You may provide a tribe to search for. If \
        no tribe is provided, a random one will be chosen.
        Examples:
        `{{pre}}letters` --> a tribe's alphabet
        `{{pre}}letters lux` --> the luxidoorian alphabet
        '''
        await ctx.send(alphabet(tribe))


    @commands.command(brief='Translate to Elyrion.')
    async def elyrion(self, ctx, *, english):
        """
        Translate text to elyrion.

        Examples:
        `{{pre}}elyrion This is what I want to convert.`
        """
        text = eng_to_ely(english)
        if ctx.guild:
            await imitate(ctx, text)
        else:
            await ctx.send(text)


    @commands.command(brief='Translate from Elyrion.')
    async def english(self, ctx, *, elyrion):
        """
        Translate text from elyrion.

        Examples:
        `{{pre}}elyrion Ŧţi^ i^ ~ţaŦ i ~aŋŦ Ŧȱ #ȱŋ‡∑rŦ.`
        """
        await ctx.send(ely_to_eng(elyrion))
